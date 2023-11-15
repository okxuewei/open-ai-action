from fastapi import FastAPI, HTTPException
from git import Repo
import os
import shutil
from pydantic import BaseModel

app = FastAPI()


# 定义请求体的模型
class GitRepo(BaseModel):
    git_url: str


@app.get("/")
async def get_main():
    return {"message": "This is the main page of the code reader API service."}


@app.post("/get-repo-content/")
async def print_repo_url(repo: GitRepo):
    print("入参 git_url " + repo.git_url)
    git_url = repo.git_url
    base_dir = f"./{git_url.split('/')[-1]}"
    try:
        # 从URL中解析仓库名称
        repo_name = git_url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        print("本地仓库地址 " + repo_name)
        repo_dir = os.path.join(base_dir, repo_name)
        print("Git仓库地址 " + repo_dir)
        # 如果目录存在，先删除
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        # 克隆仓库
        Repo.clone_from(git_url, repo_dir)

        print("克隆仓库 完成")
        content = read_all_files(repo_dir)

        print("读取仓库 完成")
        # 清理克隆的仓库目录
        try:
            shutil.rmtree(repo_dir)
        except:
            pass

        return {"content": content[:50000]}

    except Exception as e:
        print("发生错误：", e)
        raise HTTPException(status_code=500, detail=str(e))


def read_all_files(directory):
    all_text = ""
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                print("read_all_files  file_path"+file_path)
                if os.path.isfile(file_path) and (file_path.endswith(".py") or file_path.endswith(".java")):
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            filename = file_path.split("/")[-1]
                            print("read_all_files  filename"+filename)
                            all_text += f"File: {filename}\n\n" + file.read() + "\n\n"
                    except UnicodeDecodeError:
                        # 忽略无法读取的文件（如二进制文件）
                        print("read_all_files  UnicodeDecodeError")
                        pass
    except Exception as e:
        print("发生错误 read_all_files：", e)
    except WindowsError:
        # 忽略无法读取的文件（如二进制文件）
        print("发生错误 read_all_files WindowsError")
        pass
    print("read_all_files  all_text"+all_text)
    return all_text


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("test_batckend_for_action:app", host="127.0.0.1", port=80)
