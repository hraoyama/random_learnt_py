#include <vector>
#include <string>
#include <iostream>
#include "../hpp/abstraction.hpp"

int main()
{
    using namespace Data;
    using Matrix2D = std::vector<std::vector<double>>;
    using Surface = std::vector<Matrix2D>;
    using IntIDCollection = DataSet<int>;
    using StringIDCollection = DataSet<std::string>;
    
    // Example usage of NamedValueHolderCollection
    std::cout << "\n=== DataSet/DataPoint Example ===" << std::endl;

    StringIDCollection collection; // identify objects by string
    // Add different types of NamedValueHolder instances to the same collection
    collection.add(42, "IntValue");
    collection.add(3.14159, "DoubleValue");
    collection.add(std::string("The Country of Great Credit Ratings"), "IssuerName");
    collection.add(std::vector<int>{1, 2, 3, 4, 5}, "IntVector1");
    collection.add(std::vector<int>{6, 7, 8, 9, 10}, "IntVector2");
    Matrix2D mat1 = { {1.5, 0.9}, {1.2, 1.25} };
    Matrix2D mat2 = { {2.6, 6.0}, {3.7, 5.41} };
    collection.add(Surface{ mat1, mat2 }, "SurfaceValues");

    std::cout << "Collection size: " << collection.size() << std::endl;
    std::cout << "Contains 'IntValue': " << (collection.contains("IntValue") ? "true" : "false") << std::endl;
    std::cout << "Contains 'NonExistent': " << (collection.contains("NonExistent") ? "true" : "false") << std::endl;

    /*
    IntIDCollection collection2;
    collection2.add(std::vector<double>{ -0.5, 0.25, 0.85, 20.5 }, 12436);
    collection2.add(Surface({ mat1, mat2 }), 9999);
    collection2.add(std::string("Secret Sauce"), 569);


    StringIDCollection collection3;
    collection3.add(95863416.46, "AnotherDoubleValue");
    
    IntIDCollection collection4;
    collection4.add(std::string("This is a couple of levels deep"), 8746993);

    //// should there be a check for circular collections? Or is that acceptable?
    collection3.add(collection4, "AVeryDeepSubset");
    collection2.add(collection3, 55555555);
    collection.add(collection2, "SubSetIdentifiedUsingInt");

    std::cout << "Collection size (collection): " << collection.size() << std::endl;
    std::cout << "Collection size (collection2): " << collection2.size() << std::endl;
    std::cout << "Collection size (collection3): " << collection3.size() << std::endl;
    std::cout << "Collection size (collection4): " << collection4.size() << std::endl;
    
    printValues<std::string, std::string>(collection, "IssuerName");

    const auto& subset2 = collection.getValue<IntIDCollection>("SubSetIdentifiedUsingInt");
    if (subset2) {
        const auto& val = subset2->get();
        // val is a shared_ptr<NamedValueHolder<IntIDCollection, ...>>
        // Get the container to access the actual IntIDCollection
        const auto& container = val->getContainer();
        if (!container.empty()) {
            for( const auto& actualCollection : container) {
                std::cout << "Subset collection size: " << actualCollection.size() << std::endl;
                int itemCounter = 1;
                // for( const auto& item : actualCollection->getContainer()) {
                //     std::cout << "Item " << itemCounter << " (" << item.name() << "): " << std::endl;
                //     ++itemCounter;
                // }
            } // Get the first (and likely only) IntIDCollection            
        }

    }
        
    */   
    //std::cout << "Contains 'NonExistent': " << (collection.contains("NonExistent") ? "true" : "false") << std::endl;

    //const auto& intVec = collection.getValue<std::vector<int>>("IntVector2"); // why does auto not work here?!

    //if (intVec) {
    //    const auto& valRef = intVec->get();
    //    std::cout << valRef << std::endl;
    //}


    // auto intVec = collection.getValue("IntVector2"); 


    //auto valOpt = importantVector.getValue("MyVector");
    //if (valOpt) {
    //    const auto& valRef = valOpt->get();        
    //    std::cout << "Retrieved value for 'MyVector' with " << valRef.size() << " entries" << std::endl;
    //    // Process valRef as needed
    //}

    return 0;
}