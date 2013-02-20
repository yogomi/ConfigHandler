#include <string>
#include <libxml++/libxml++.h>

namespace xmlch
{
class Config
{
public:
    Config();
    Config(const std::string&);
    ~Config();

    void open(const std::string&);

};
} //xmlch END
