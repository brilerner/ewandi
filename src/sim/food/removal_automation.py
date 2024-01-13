def remove_unwanted_foods(foods, avoid, n=5):
    """
    VERIFY THIS WORKS
    """

    def remove_foods(foods):
        def check_name_match(name, description):
            if name.lower() in description.lower():
                return True

        def check_cat_match(cat, description):
            if cat.lower() in description.lower():
                return True

        def is_food_ok(food):
            for c in avoid["categories"]:
                if check_cat_match(c, food["foodCategory"]["description"]):
                    return False
            for n in avoid["names"]:
                if check_name_match(n, food["description"]):
                    return False
            return True

        return [f for f in foods if is_food_ok(f)]

    def reduce_foods(foods):
        from collections import defaultdict

        food_types = defaultdict(list)
        for f in foods:
            description = f["description"]
            food_type = description.split(",")[0]
            if food_type[-1] == "s":
                food_type = food_type[:-1]
            food_types[food_type].append(f)

        # reduce to n foods per food type
        for k, v in food_types.items():
            food_types[k] = v[:n]

        return [f for v in food_types.values() for f in v]

    foods = remove_foods(foods)
    foods = reduce_foods(foods)

    return foods


# this is supposed to remove a name if in description unless it is in keep_name
# but it is not working
# def remove_foods(foods):

#     def check_name_match(name,description):


#         if type(name) == tuple:
#             # print(name)
#             name = name[0]
#             keep_name = name[1]
#         else:
#             keep_name = ''

#         name = name.lower()
#         description = description.lower()
#         keep_name = keep_name.lower()
#         # if description[-1] == 's':
#         #     string = string[:-1]
#         # if name[-1] == 's':
#         #     name = name[:-1]

#         if name in description:
#             if keep_name not in description:
#                 return True
