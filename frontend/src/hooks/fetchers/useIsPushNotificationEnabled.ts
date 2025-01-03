import { useDontManageGetCall } from 'dontmanage-react-sdk'

const useIsPushNotificationEnabled = () => {

    const { data } = useDontManageGetCall<{ message: boolean }>('raven.api.notification.are_push_notifications_enabled', undefined, undefined, {
        revalidateIfStale: true,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    })

    return data?.message ? true : false
}

export default useIsPushNotificationEnabled

