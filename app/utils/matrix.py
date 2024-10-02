import os
import time

import numpy as np


def generate_unitary_matrix(n):
    A = np.random.rand(n, n) + 1j * np.random.rand(n, n)
    Q, _ = np.linalg.qr(A)
    print(Q)
    return Q


def pad_data(data: dict, target_size: int, complex_matrix: bool = False) -> tuple:
    """
    Дополняем данные солью до нужного размера.
    """
    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]

    data_values = np.array(numeric_values, dtype=complex if complex_matrix else float)

    padding_size = target_size - len(data_values)

    if padding_size > 0:
        salt = np.random.rand(padding_size) + 1j * np.random.rand(padding_size) if complex_matrix else np.random.rand(
            padding_size)
        padded_data = np.concatenate((data_values, salt))
    else:
        padded_data = data_values
        salt = np.array([])  # если дополнения не требуется, соль пустая

    return padded_data, salt


def encode_data(data: dict, matrix: np.ndarray, complex_matrix: bool = False) -> tuple:
    """
    Кодирует данные с использованием унитарной матрицы.
    """
    padded_data, salt = pad_data(data, matrix.shape[1], complex_matrix=complex_matrix)
    print("Вывод матрицы из encode_data:", matrix.shape[1])
    encoded_data = np.dot(matrix, padded_data)
    return encoded_data, salt