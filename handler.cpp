#include <iostream>
#include <string>
#include <boost/python.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>

#include "handler.hpp"

namespace xmlch
{

Config::Config()
{
    return;
}

Config::Config(const std::string& s)
{
    std::cout << s << std::endl;
    return;
}

Config::~Config()
{
    return;
}

void Config::open(const std::string& s)
{
    std::cout << s << std::endl;
    return; 
}

} //xmlch END


BOOST_PYTHON_MODULE(XMLConfHandler)
{
    using namespace xmlch;
    using namespace boost::python;
    class_<Config>("XMLConfig")
        .def("open", &Config::open);
}

