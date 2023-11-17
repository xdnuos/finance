def string_generator(data_incoming):
	data = data_incoming.copy()
	del data['hash']
	keys = sorted(data.keys())
	string_arr = []
	for key in keys:
		string_arr.append(key+'='+data[key])
	string_cat = '\n'.join(string_arr)
	return string_cat
def convert_dict_to_list(rows, selected_keys):
    uniq_keys = set(selected_keys)  # sử dụng các keys đã chọn
    keys = []  # lưu trữ cho bộ
    index_key = 'Index'  # Key 'Index'

    # Kiểm tra xem có key 'Index' trong danh sách các keys đã chọn hay không
    if index_key in uniq_keys:
        keys.append(index_key)
        uniq_keys.remove(index_key)  # Loại bỏ 'Index' khỏi danh sách để tránh lặp lại

    for row in rows:
        for k in row.keys():
            # Lưu trữ items duy nhất theo thứ tự đầu vào
            if k in uniq_keys and k not in keys:
                keys.append(k)

    # Chắc chắn 'Index' sẽ xuất hiện ở đầu danh sách keys nếu nó có trong danh sách các keys đã chọn
    result = [[row.get(k) for k in keys] for row in rows]

    return result
def add_index(list_dict,start_index=0):
    for index, dictionary in enumerate(list_dict):
        dictionary["Index"] = index+start_index
    return list_dict
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
def convert_array_to_dict(data):
    if data is None:
        return []
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]]