// clang -S -emit-llvm strikert.c
#include <stdio.h>

void print_i32(int i) {
    printf("%d\n", i);
}

int mul_i32(int a, int b) {
    return a * b;
}
