def extract_values(data, key):
    """
    Chuyển đổi danh sách các từ điển thành danh sách các giá trị của khóa cụ thể.

    Parameters:
    - data: Danh sách các từ điển.
    - key: Khóa cần trích xuất giá trị.

    Returns:
    - Danh sách các giá trị của khóa cụ thể.
    """
    return [item[key] for item in data]
new =extract_values([{"id":2},{"id":4}], 'id')
print(new)
