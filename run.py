import subprocess
import pandas as pd
from tqdm import tqdm

if __name__ == '__main__':

    df = pd.read_csv("Companies_436_Sheet1.csv")
    count = 0
    for i in tqdm(range(df.shape[0])):
        cmp = df.iloc[i, 0]
        link = df.iloc[i, 2]
        if cmp == 'Unqork':
            count =1
            continue
        if not count:
            continue

        print(f"cmp : {cmp}, link: {link}")
    # cmp = 'snyk'
    # link = 'https://boards.greenhouse.io/snyk/' #https://snyk.io/careers/all-jobs/ ?
        if link == link:
            subprocess.run(["python", "pipeline.py", "--company", cmp,  "--seed_link", link])