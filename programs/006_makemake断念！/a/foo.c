#include <stdio.h>
#include "hello.h"
#include "foo.h"

extern void foo0(void);
void foo1(void) 
{
    foo0();
    printf("foo1()\n");
}
