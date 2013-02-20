#include <string>
#include <boost/property_tree/ptree.hpp>

namespace xmlch
{
class Config
{
public:
    Config();
    ~Config();

    void open(const std::string&);
    void read(const std::string&);
    void getElements(const std::string&);
private:
    boost::property_tree::ptree _tree;
};
} //xmlch END
