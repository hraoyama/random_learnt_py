import pandas as pd
import polars as pl
import pyarrow as pa
import numpy as np
import redis
import functools
import pickle
import json
import hashlib
from io import StringIO, BytesIO

class RolarsCache(object):

    _ACCEPTABLE_METHODS = ['pickle', 'pyarrow', 'json']

    def refresh(self):
        # storing of keys in the object so as to know how to retrieve the value
        # Scan for all keys matching the pattern and extract their serialization method
        keys_already_present = []
        for k in self.cache_container.scan_iter(match=f"{self.leading_key}-*"):
            key_str = k.decode() if isinstance(k, bytes) else k
            # Key format: RolarsCache-{method}-{func_name}|...
            parts = key_str.split('-')
            if len(parts) >= 3:
                method = parts[1]  # Extract method (pickle, pyarrow, json)
                keys_already_present.append((key_str, method))
        self.keys = dict(keys_already_present)

    def __init__(self, redis_instance, key=None, hash_keys=False):
        # Checks that a redis object has been passed
        # https://stackoverflow.com/questions/57949871/how-to-set-get-pandas-dataframes-into-redis-using-pyarrow/57986261#57986261
        if isinstance(redis_instance, redis.client.Redis) !=True:
            raise AttributeError(
                "Did not recieve an Redis Object, instead received {}".format(type(redis_instance)))

        # Sets the redis object as an attribute of this class
        self.cache_container = redis_instance

        # leading for reference in db, can be used to identify the caching object in redis
        self.leading_key = 'RolarsCache'

        # Key to identify object/state of object,
        # if None, key will try to be generated from inputs of function
        self.key=key

        assert isinstance(hash_keys, bool), "[ERROR]: hash_keys should be a bool"
        self.hash_keys=hash_keys
        
        self.refresh()


    #------------------------------------------------------------------------------------
    # Internal Methods for mananging posting and getting from redis
    #------------------------------------------------------------------------------------
    @staticmethod
    def _hashing_key(*args):
        """
        Creates a hash of the object given to create unique id
        using the sha256 algorith
        Parameters:
        -----------
            args=must be able represented as a str
        Returns:
        --------
            str(), hash of the inputs
        """
        # flattens args in case of a list is in the value
        values=[]
        for i in args:
            if isinstance(i, list):
                for j in i:
                    list_values=[]
                    # Checks if value in list is none
                    if j is not None:
                        # Adds to cleaned list values
                        list_values.append(str(j))
                # Sort inner list before adding to params values
                if len(list_values)>0:
                    sorted(list_values)
                    for x in list_values:
                        values.append(x)
            else:
                values.append(str(i))

        #Creates a key for redis cache
        # URL: https://www.pythoncentral.io/hashing-strings-with-python/
        key=', '.join(values)
        generated_key=hashlib.sha256(key.encode())
        generated_key=generated_key.hexdigest()
        return generated_key


    def key_generator(self, func, method, *args, **kwargs):
        """
        Generates a key for redis to cache based on the function
        it will decorate as well as the inputs to that function
        Returns:
            str()
        """
        leading = f"{self.leading_key}-{method}-{func.__name__}"

        params=[]
        # Cleaning up args
        if len(args) > 0:
            args_given = [str(i) for i in args]
            args_given = '|'.join(args_given)
            params.append(args_given)

        # Cleaning up kwargs
        if len(kwargs) > 0 and self.hash_keys==False:
            for i in kwargs.keys():
                params.append(f"({i}-{kwargs[i]})")

        # Hashes key with sha256 to generate a unique id
        if self.hash_keys==True:
            # Takes list of params and joins into unique id string
            params=RolarsCache._hashing_key(params)
            key=[leading, params]

        else:
            # Inserts the leading key and func string as prefix
            params.insert(0, leading)
            key = params

        return "|".join(key) # ":".join(key)

    def _deserialize(self, key):
        """
        Method for deserializing python object
        Parameters:
        -----------
            key=value to use in the redis cache
        Returns:
        --------
            python object
        """
        
        #         table = pa.deserialize(r.get("polars_df"))
        # df = pl.from_arrow(table)
        
        pull_value = self.cache_container.get(key)

        # If key found, and not passed through object, return serialized object
        if key not in self.keys.keys():
            self.refresh()

        if key not in self.keys.keys():
            return pickle.loads(pull_value)

        if self.keys[key]=='pickle':
            value=pickle.loads(pull_value)
        elif self.keys[key]=='pyarrow':
            # Use PyArrow IPC format for deserialization (compatible with PyArrow 22.0.0+)
            reader = pa.ipc.open_stream(pull_value)
            arrow_table = reader.read_all()
            value = pl.from_arrow(arrow_table)  # even if it was a pandas dataframe that got serialized, it gets deserialized as a polars object
        elif self.keys[key]=='json':
            value=json.loads(pull_value)
            # value=pl.read_json(StringIO(json.loads(pull_value))) # json serialization is not just polars?
        return value


    def _serialize(self, key, value):
        """
        Method for serializing python object
        Parameters:
        -----------
            key: value to use in the redis cache
            value: object to serialize            
        Returns:
        --------
            python object
        """
        # Auto-detect method if not provided
        method = key.split('-')[1].lower() if key.startswith(f"{self.leading_key}-") else "pickle"
        
        # Get type checks for serialization logic
        is_polars_value = isinstance(value, pl.DataFrame) or isinstance(value, pl.Series) or isinstance(value, pl.LazyFrame) or isinstance(value, pl.LazySeries)
        is_pandas_value = isinstance(value, pd.DataFrame) or isinstance(value, pd.Series)
        is_numpy_value = isinstance(value, np.ndarray) or isinstance(value, np.matrix) or isinstance(value, np.recarray)
        
        if method=='pickle':
            hashed_value=pickle.dumps(value)
            self.keys[key]='pickle'

        elif method=='pyarrow':
            if is_polars_value or is_pandas_value:
                # Use PyArrow IPC format for serialization (compatible with PyArrow 22.0.0+)
                arrow_table = None
                if is_polars_value:
                    arrow_table = value.to_arrow()
                else:
                    arrow_table = pa.Table.from_pandas(value)
                sink = BytesIO()
                writer = pa.ipc.new_stream(sink, arrow_table.schema)
                writer.write_table(arrow_table)
                writer.close()
                hashed_value = sink.getvalue()
            else:
                # Fallback to pickle for non-DataFrame/Series types
                hashed_value = pickle.dumps(value)
                method = 'pickle'
            self.keys[key]='pyarrow'

        elif method=='json':
            hashed_value = json.dumps(value) # json.dumps(value.to_json())  # json serialization is not just polars?
            self.keys[key]='json'

        self.cache_container.set(key, hashed_value)

    #------------------------------------------------------------------------------------
    # GET and POST methods to send and retrive objects from cache
    #------------------------------------------------------------------------------------
    def get(self, key):
        """
        Returns object from the redis database if key exists
        """
        if self.cache_container.exists(key) == 1:
            return self._deserialize(key)
        else:
            raise ValueError("No key {} found in object".format(key))


    def post(self, key, values, serialization='pyarrow'):# serialization='pickle'):
        """
        Posts key,value to redis where its serilaized by the serialization param
        Parameters:
        -----------
            key=str()
            values=python object
            serialization=str(), of which is 'pickle', 'json', 'pyarrow'
        Returns:
        --------
            python object
        """
        assert isinstance(key, str)
        assert isinstance(serialization,str)
        assert serialization in ['pickle', 'json', 'pyarrow']

        self._serialize(key, values, method=serialization)
    #------------------------------------------------------------------------------------
    # Caching Decorators to be used over functions
    #------------------------------------------------------------------------------------

    def cache(self, method='pyarrow', func=None):
        """
        General Decorater function for caching functions, will attempt to cache with the
        correct serialization based on type, else use pickle
        
        Usage:
            @cache.cache(method='pyarrow')
            def my_function():
                return pl.DataFrame(...)
        
        Parameters:
            method: str, one of ['pickle', 'pyarrow', 'json']
            func: python function (used internally by decorator)
        Returns:
            Python Object
        """
        # If func is provided, we're being called directly (old-style decorator)
        if func is not None:
            assert method in RolarsCache._ACCEPTABLE_METHODS
            return self._apply_cache_decorator(func, method)
        
        # Otherwise, we're being used as @cache.cache(method='pyarrow')
        # Return a decorator function
        assert method in RolarsCache._ACCEPTABLE_METHODS
        
        def decorator(f):
            return self._apply_cache_decorator(f, method)
        return decorator
    
    def _apply_cache_decorator(self, func, method):
        """Helper method that applies the caching decorator logic"""
        @functools.wraps(func)
        def wrapper_df_decorator(*args, **kwargs):
            # generate key based on called function
            if self.key==None:
                key=self.key_generator(func, method, *args, **kwargs)
            else:
                key=self.key_generator(func, method, self.key)

            # check if exists in redis
            if self.cache_container.exists(key) == 1:
                # Pulls data from redis, deserialses and returns the dataframe
                value = self._deserialize(key)
            else:
                # Runs the function that was decorated
                value = func(*args, **kwargs)
                # Serialize the value (method is auto-detected in _serialize)
                self._serialize(key, value)

            return value
        return wrapper_df_decorator


    def json_cache(self, func):
        """
        Decorater function for caching functions with json serialization
        Recommended to be used with dict style objects
        Refer to the python json api for more info
        Parameters:
            func = python function, is the input due to wrapping
        Returns:
            Python Object (cld used for pandas, numpy?)
        """
        @functools.wraps(func)
        def wrapper_df_decorator(*args, **kwargs):
            # generate key based on called function
            method = 'json'
            if self.key==None:
                key=self.key_generator(func, method, *args, **kwargs)
            else:
                key=self.key_generator(func, method, self.key)

            # check if exists in redis
            if self.cache_container.exists(key) == 1:
                # Pulls data from redis, deserialses and returns the dataframe
                value = self._deserialize(key)
            else:
                # Runs the function that was decorated
                value = func(*args, **kwargs)
                self._serialize(key, value, method='json')

            return value
        return wrapper_df_decorator

    def pyarrow_cache(self, func):
        """
        Decorater function for caching functions with pyarrow serialization
        Recommended to be used with pandas, numpy or any table style object
        Refer to pyarrow for more specification
        Parameters:
            func = python function, is the input due to wrapping
        Returns:
            Python Object
        """
        @functools.wraps(func)
        def wrapper_df_decorator(*args, **kwargs):
            # generate key based on called function
            method = 'pyarrow'
            if self.key==None:
                key=self.key_generator(func, method, *args, **kwargs)
            else:
                key=self.key_generator(func, method, self.key)

            # check if exists in redis
            if self.cache_container.exists(key) == 1:
                # Pulls data from redis, deserialses and returns the dataframe
                value = self._deserialize(key)
            else:
                # Runs the function that was decorated
                value = func(*args, **kwargs)
                self._serialize(key, value, method='pyarrow')

            return value
        return wrapper_df_decorator

if __name__ == "__main__":
    import polars as pl
    import pyarrow as pa
    import redis
    from pprint import pprint as pp

    r = redis.Redis(host='localhost', port=6379, db=0)

    cache = RolarsCache(r)

    # @cache.cache(method='pyarrow')
    # def test(key, num):
    #     df=pl.DataFrame({'A':range(1,num+1,1)})
    #     return df
    # a = test('key', 4)
    
    df = cache.get('RolarsCache-pyarrow-test|key|4')
    pp(df)
    
    
    
    
    
