#include <iostream>
#include <type_traits>
#include <concepts>
#include <optional>
#include <map>
#include <memory>
#include <vector>
#include <limits>
#include <set>

namespace Data {

    template<typename T>
    concept HasAssignmentOperator = requires(T a, T b) {
        a = b;
    };

    template<typename IDType = std::string>
    requires std::totally_ordered<IDType> && std::copyable<IDType> && HasAssignmentOperator<IDType>
    class Identifiable
    {
    protected:
        IDType idvalue;
    public:
        Identifiable(const IDType& n) : idvalue(n) {}
        const IDType& id() const { return idvalue; }
        void reassign(const IDType& n) { idvalue = n; }
    };

    class TypedDataPointWrapper
    {
    public:
        virtual ~TypedDataPointWrapper() = default;
        virtual const std::type_info& get_type() const = 0;
        virtual void* get_void_ptr() = 0;
        virtual const void* get_void_ptr_const() const = 0;
    };

    template<typename T, typename IDType = std::string>
    requires std::copyable<T>
    class DataPoint : public Identifiable<IDType>, public TypedDataPointWrapper
    {
    private:
        const T& data = {};
    public:
        explicit DataPoint(const T& input, const IDType& id) : Identifiable<IDType>(id), data(input) {}
        // DataPoint-specific functions
        operator const T& () const { return data; }
        const T& get_typed() const { return data; }

        T copy() const { return data; }
        const T& getValue() const { return data; }
        
        const std::type_info& get_type() const override {
            return typeid(T);
        }
        void* get_void_ptr() override {
            return const_cast<T*>(&this->get_typed());
        }
        const void* get_void_ptr_const() const override {
            return &this->get_typed();
        }
    };

    // Helper function to safely retrieve and cast typed data
    template<typename T, typename IDType = std::string>
    std::optional<std::reference_wrapper<const T>> try_get_as(
        const std::shared_ptr<TypedDataPointWrapper>& wrapper)
    {
        if (wrapper && wrapper->get_type() == typeid(T)) {
            auto typed_ptr = static_cast<DataPoint<T, IDType>*>(wrapper.get());
            return std::cref(typed_ptr->get_typed());
        }
        return std::nullopt;
    }

    template<typename IDType = std::string, typename IDTypeCollection = std::string>
    class DataSet : Identifiable<IDType>
    {
    private:
        std::set<std::shared_ptr<Identifiable<IDTypeCollection>>> collection{};
        // not possible to have a nullptr b/c we block its addition
    public:
        DataSet() : Identifiable<IDType>(IDType{}) {}

        bool contains(const IDTypeCollection& key) const {
            for (const auto& element : collection) {
                if (key == element->id()) {
                    return true;
                }
            }
            return false;
        }

        template<typename T>
        bool add(const DataPoint<T, IDTypeCollection>& dp) {
            if (contains(dp.id())) {
                return false; // already exists
            }
            collection.insert(std::make_shared<DataPoint<T, IDTypeCollection>>(dp));
            return true;
        }

        template<typename T>
        bool add(const T& value, const IDTypeCollection& key) {
            if (contains(key)) {
                return false; // already exists
            }
            DataPoint<T, IDTypeCollection> dp(value, key);
            collection.insert(std::make_shared<DataPoint<T, IDTypeCollection>>(dp));
            return true;
        }

        template<typename IDTypeSubCollection>
        bool add(const DataSet<IDTypeCollection, IDTypeSubCollection>& ds) {
            if ( ds == this ) {
                return false; // prevent circular reference
            }
            if (contains(ds.id())) {
                return false; // already exists
            }
            collection.insert(std::make_shared<DataSet<IDTypeCollection, IDTypeSubCollection>>(ds));
            return true;
        }

        size_t size() const { return collection.size(); }

        std::vector<IDTypeCollection> getIds() {
            std::vector<IDTypeCollection> ids;
            for (const auto& element : collection) {
                ids.push_back(element->id());
            }
            return ids;
        }

        // Get a value from the collection by key and type
        template<typename T>
        auto getValue(const IDType& key) const {
            for (const auto& element : collection) {
                if (key == element->id()) {
                    return element->template getValue<T>();
                }
            }
            return std::numeric_limits<T>::quiet_NaN();
        }

        // Clear the collection
        void clear() { collection.clear(); }
    };


    // template<typename ReturnType, typename IdentifierType>
    // void printValues(const auto& collection, const IdentifierType& identifier)
    // {
    //     const auto& optRetrievedValue = collection.template getValue<ReturnType>(identifier);
    //     if (optRetrievedValue) {
    //         const auto retrievedValue = optRetrievedValue->get();
    //         const auto& containerWithValues = retrievedValue->getContainer();
    //         std::cout << "Retrieved value for " << identifier << " with " << containerWithValues.size() << " entries" << std::endl;

    //         int itemCounter = 1;
    //         for (const auto& inContVal : containerWithValues) {
    //             std::cout << "Item " << itemCounter << ": " << inContVal << std::endl;
    //             ++itemCounter;
    //         }

    //     }
    // }





}