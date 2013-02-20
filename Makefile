TARGET=XMLConfHandler.so

SRCS=handler.cpp
OBJS=$(SRCS:.cpp=.o)

INCLUDES:=$(shell xml2-config --cflags)
INCLUDES+= -I/usr/lib/glib-2.0/include -I/usr/include/glib-2.0 -I/usr/lib/glibmm-2.4/include -I/usr/lib/libxml++-2.6/include -I/usr/include/glibmm-2.4 -I/usr/include/libxml++-2.6 -fPIC -I/usr/include/python2.6
LIBS:=$(shell xml2-config --libs)
LIBS+= -lglibmm-2.4 -lxml++-2.6 -lpython2.6 -lboost_python

CFLAGS= -Wall
CXXFLAGS= $(CFLAGS) $(INCLUDES)
CXX=g++

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -shared $(LIBS) -o $@ $^

clean:
	rm $(OBJS)
	rm $(TARGET)

.PHONY: all install clean
