#include <string>
#include <boost/python.hpp>
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
    std::string getAttr(const std::string& tag, const std::string& key);
    boost::python::dict getAttrDict(const std::string&);
    void setElements(const boost::python::dict&);
private:
    boost::property_tree::ptree _tree;
    std::string _filename;
};
} //xmlch END
