from waimaiapp.models import Customer, Driver

def create_user_by_type(backend, user, request, response, *args, **kwargs):
    request = backend.strategy.request_data()
    if backend.name == 'facebook':
        avatar = 'https://graph.facebook.com/%s/picture?type=large' % response['id']
    # else:
    #     avatar = ''

        if request['user_type'] == "driver" and not Driver.objects.filter(user_id=user.id):
            Driver.objects.create(user_id=user.id, avatar = avatar)
        elif not Customer.objects.filter(user_id=user.id):
            Customer.objects.create(user_id=user.id, avatar = avatar)
            # print(request['user_type'])