#include <iostream>
#include <omp.h> // NEW ADD

using namespace std;

int main()
{
int sum = 0;
#pragma omp parallel for num_threads(4) reduction(+:sum) // NEW ADD
    
    for (int i = 0; i <= 10000; i++)
    {
        sum += 1;
    }

    cout << sum << endl;
    return 0;
}