#include <iostream>
#include <string>
#include <boost/python.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>

#include "handler.hpp"

namespace xmlch
{

using namespace boost::property_tree;

Config::Config()
{
    return;
}

Config::~Config()
{
    return;
}

void Config::open(const std::string& filename)
{
    read_xml(filename, _tree);
    return; 
}

void Config::read(const std::string& key)
{
    if(boost::optional<std::string> str = _tree.get_optional<std::string>(key)){
        std::cout << str.get() << std::endl;
    }else{
        std::cout << "no property: " << key << std::endl;
    }
    return;
}

void Config::getElements(const std::string& tagname)
{
    if(boost::optional<std::string> str = _tree.get_optional<std::string>(tagname)){
        std::cout << str.get() << std::endl;
    }else{
        std::cout << "no property: " << std::endl;
    }
    return; 
}

} //xmlch END


BOOST_PYTHON_MODULE(XMLConfHandler)
{
    using namespace xmlch;
    using namespace boost::python;
    class_<Config>("XMLConfig")
        .def("open", &Config::open)
        .def("read", &Config::read)
        .def("getElements", &Config::getElements)
        ;
}

