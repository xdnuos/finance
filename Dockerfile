# Sử dụng hình ảnh Python
FROM python:3.10.10

# Sao chép mã nguồn vào thư mục /app trong container
COPY . /app

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện cần thiết
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Chạy ứng dụng khi container khởi động
CMD ["python", "main.py"]
