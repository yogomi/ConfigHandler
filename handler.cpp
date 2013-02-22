#include <iostream>
#include <string>
#include <boost/python.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>

#include "handler.hpp"

namespace xmlch
{

using namespace boost::python;
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
    _filename = filename;
    read_xml(_filename, _tree);
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

std::string Config::getAttr(const std::string& tag, const std::string& key)
{
    return _tree.get<std::string>(tag + ".<xmlattr>." + key);
}

dict Config::getAttrDict(const std::string& tag)
{
    ptree pt = _tree.get_child(tag + ".<xmlattr>");
    iterator aa = pt.iterator.begin();
    //std::cout << pt.iterator.first << std::endl;
    //iterator it = pt.iterator.begin();
    //auto end = keys.end();
    //for(; it!=end; ++it){
    //    std::cout << pt.first << std::endl;
    //}
    return dict();
}

void Config::setElements(const dict& dic)
{
    list l = dic.keys();
    std::cout << len(l) << std::endl;
    for( int i=0; i<len(l); i++ ){
        std::string a = extract<std::string>(l[i]);
        std::cout << a << std::endl;
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
        .def("getAttr", &Config::getAttr)
        .def("getAttrDict", &Config::getAttrDict)
        .def("setElements", &Config::setElements)
        ;
}

