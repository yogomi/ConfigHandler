TARGET=XMLConfHandler.so

SRCS=handler.cpp
OBJS=$(SRCS:.cpp=.o)

INCLUDES:=$(shell python2.6-config --includes)
INCLUDES+= -fPIC
LIBS:=$(shell python2.6-config --libs)
LIBS+= -lboost_python

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
