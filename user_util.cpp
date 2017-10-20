#include <string>

bool is_reply(std::string subject) {
  return subject.substr(0, 3) == "Re:" || subject.substr(0, 3) == "RE:"
         || subject.substr(0, 3) == "re:";
}
