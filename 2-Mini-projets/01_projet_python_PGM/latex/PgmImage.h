#include <iostream>
#include <fstream>
#include <cmath>
#include <string>
#include <utility>  // swap
#include <vector>

#include <boost/format.hpp>
#include <boost/timer/timer.hpp>


using namespace std;

typedef unsigned char uint8;

#ifndef PGM
#define PGM

class PgmImage{
public:
    PgmImage(size_t w=0, size_t h=0, size_t lev=255);
    PgmImage(const PgmImage& other);
    virtual ~PgmImage();

    PgmImage& operator=(const PgmImage& other);

    size_t getwidth();
    size_t getheight();
    size_t getsize();

    void fillConst(double value);
    void fillSine(const double Tx, const double Ty);
    void autoCB();
    void clamp(const double value);

    virtual void write(string nom, string mode="ascii");
    virtual void read(string nom);

private:
    size_t width_, height_, maxlev_;	
    uint8* data_;
    void extrema(size_t& min, size_t& max);
};

#endif


