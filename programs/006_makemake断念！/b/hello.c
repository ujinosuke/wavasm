#include <stdio.h>
#include "hello.h"
#include "foo.h"

extern void foo1(void);
int main(void)
{
    printf("Hello World\n");
    foo1();
}
void foo0(void)
{
    printf("foo0()\n");
}

