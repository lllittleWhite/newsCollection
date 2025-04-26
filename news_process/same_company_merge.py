import pandas as pd

def sort_by_company(input_path, output_path=None):
    """
    将相同公司名的数据按字典序连续排列
    
    参数:
    input_path -- 输入CSV路径
    output_path -- 输出CSV路径
    """
    if output_path is None:
        output_path = input_path
    df = pd.read_csv(input_path)
    df_sorted = df.sort_values(by='company')
    df_sorted.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # 打印前10行
    print(df_sorted.head(10))
    return output_path

if __name__ == "__main__":
    input_file = "news_data_store/test_data/raw_data_250415.csv"
    output_file = "news_data_store/test_data/raw_data_250415.csv"
    
    # 选择排序方式
    sort_by_company(input_file, output_file)