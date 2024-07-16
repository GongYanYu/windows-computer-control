import os

default_settings = {
    # Aes 解密密钥
    "key":"123456",
}
# 保存设置目录
settings_folder = 'user_settings'
settings_name = 'config.txt'
settings_is_loading_file = False

# ---dev True  ---release False


def update_settings(obj):
    global default_settings, settings_folder, settings_name

    default_settings = obj
    if not os.path.exists(settings_folder):
        os.makedirs(settings_folder)
    with open(settings_folder + '/' + settings_name, 'w', encoding="utf-8") as f:
        f.write(str(obj))
    return True


def read_settings():
    global default_settings, settings_folder, settings_name, settings_is_loading_file
    if not settings_is_loading_file:
        if not os.path.exists(settings_folder):
            # 第一次创建文件夹与文件
            os.makedirs(settings_folder)
            update_settings(default_settings)
        else:
            # 读取
            with open(settings_folder + '/' + settings_name, 'r', encoding="utf-8") as f:
                default_settings = eval(f.read())
        print("本地配置读取完成")
        settings_is_loading_file = True
    return default_settings


if __name__ == '__main__':
    print(read_settings())
