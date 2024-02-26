import uvicorn
from fastapi import FastAPI
from endpoints import router

app = FastAPI()


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)


# from other import first, months, second


# def merge_dict(dict1, dict2):  # объединяет валидированные словари в один
#     for key, val in dict1.items():
#         if type(val) is dict:
#             if key in dict2 and type(dict2[key] == dict):
#                 merge_dict(dict1[key], dict2[key])
#         else:
#             if key in dict2:
#                 dict1[key] = dict2[key]

#     for key, val in dict2.items():
#         if key not in dict1:
#             dict1[key] = val
#     return dict1

# first = dict_check(first, pattern_date, pattern_term)
# second = dict_check(second, pattern_date, pattern_term)

# dictik = merge_dict(first, second)
# # print(dictik)
