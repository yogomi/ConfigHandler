TARGET=XMLConfHandler.so

SRCS=handler.cpp
OBJS=$(SRCS:.cpp=.o)

#INCLUDES:=$(shell xml2-config --cflags)
INCLUDES+= -fPIC -I/usr/include/python2.6
#LIBS:=$(shell xml2-config --libs)
LIBS+= -lpython2.6 -lboost_python

CFLAGS= -Wall
CXXFLAGS= $(CFLAGS) $(INCLUDES)
CXX=g++

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -shared $(LIBS) -o $@ $^
	mkdir -p lib
	cp $@ lib/

install: $(TARGET)
	cp $(TARGET) test/

clean:
	rm -r lib
	rm $(OBJS)
	rm $(TARGET)

.PHONY: all install clean
