#include <stdio.h>
extern void foo0(void);
void foo1(void) 
{
    foo0();
    printf("foo1()\n");
}
