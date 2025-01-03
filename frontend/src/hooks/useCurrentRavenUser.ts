import { RavenUser } from '@/types/Raven/RavenUser'
import { useDontManageGetCall } from 'dontmanage-react-sdk'

const useCurrentRavenUser = () => {

    const { data, mutate } = useDontManageGetCall<{ message: RavenUser }>('raven.api.raven_users.get_current_raven_user',
        undefined,
        'my_profile',
        {
            // revalidateIfStale: false,
            revalidateOnFocus: false,
            shouldRetryOnError: false,
            revalidateOnReconnect: true
        }
    )

    return {
        myProfile: data?.message,
        mutate
    }

}

export default useCurrentRavenUser