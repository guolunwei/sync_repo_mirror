import os


def get_all_env_vars():
    """
    Get and print all environment variables.

    :return: None
    """
    env_vars = os.environ
    for k, v in env_vars.items():
        print(f"{k}: {v}")
<<<<<<< HEAD
=======


# get_all_env_vars()
>>>>>>> 7bb864d671343656653df57557a303182d2f7b8d
