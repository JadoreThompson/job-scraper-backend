if __name__ == "__main__":
    from clean import _count
    import pandas as pd
    
    
    df = pd.read_csv('example.csv')
    print('Language: ', _count(['python', 'java', 'c++', 'c'], df))
    print('Degree: ', _count(['bachelors'], df))
    print('AI Count: ', _count(['machine learning', 'ai'], df))
    print('Finance Count: ', _count(['finance', 'trading'], df))    
