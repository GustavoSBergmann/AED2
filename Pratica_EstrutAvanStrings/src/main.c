#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "hat-trie.h"
#include <stdbool.h>

#define ALFABETO 26

typedef struct TrieNode
{
    struct TrieNode *filhos[ALFABETO];
    bool fim_palavra;
} TrieNode;

int main(int argc, char const *argv[])
{
    printf("Hello World!\n");

    return 0;
}
