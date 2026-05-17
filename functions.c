#include <stdio.h>
#include <stdlib.h>
#include <math.h>


float* calculate_distances(short* array[], int m_size){
    short i;
    short k;

    float* matrix = malloc(sizeof(float) * m_size * m_size);

    for(i = 0; i < m_size; i++){
        short* i_point = array[i];
        for(k = i; k < m_size; k++){
            if (i == k){matrix[i * m_size + k] = 50000; continue;}
            // matrix[i * m_size + k] = (float) sqrt(pow((i_point[0] - array[k][0]), 2) + pow((i_point[1] - array[k][1]), 2));
            matrix[i * m_size + k] = (float) (abs((i_point[0] - array[k][0])) + abs((i_point[1] - array[k][1])));
        }
    }

    for(i = 0; i < m_size; i++){
        for(k = 0; k < i; k++){
            matrix[i * m_size + k] = matrix[k * m_size + i];
        }
    }

    return matrix;
}

float* calculate_vector(short target_point[2],  short* array[], short size){
    printf("target_point - %d %d", target_point[0], target_point[1]);
    short arr_size = size;
    float* out_array = malloc(sizeof(float) * arr_size);

    short i;
    for(i = 0; i < arr_size; i++){
        out_array[i] = (float) (abs(target_point[0] - array[i][0]) + abs(target_point[1] - array[i][1]));
    }
    return out_array;
}

