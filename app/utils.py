def string_generator(data_incoming):
	data = data_incoming.copy()
	del data['hash']
	keys = sorted(data.keys())
	string_arr = []
	for key in keys:
		string_arr.append(key+'='+data[key])
	string_cat = '\n'.join(string_arr)
	return string_cat
def convert_dict_to_list(rows):
    uniq_keys = set()  # implements hashed lookup
    keys = []  # storage for set
    for row in rows:
        for k in row.keys():
            # Save unique items in input order
            if k not in uniq_keys:
                keys.append(k)
                uniq_keys.add(k)
    return [[row.get(k) for k in keys] for row in rows]
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