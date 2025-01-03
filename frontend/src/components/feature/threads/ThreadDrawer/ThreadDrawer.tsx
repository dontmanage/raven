import { Box, Flex } from '@radix-ui/themes'
import { useParams } from 'react-router-dom'
import { ThreadMessages } from './ThreadMessages'
import { useDontManageGetDoc } from 'frappe-react-sdk'
import { ErrorBanner } from '@/components/layout/AlertBanner/ErrorBanner'
import { FullPageLoader } from '@/components/layout/Loaders/FullPageLoader'
import { ThreadHeader } from './ThreadHeader'
import { Message } from '../../../../../../types/Messaging/Message'

const ThreadDrawer = () => {

    const { threadID } = useParams()
    const { data, error, isLoading } = useDontManageGetDoc<Message>('Raven Message', threadID, threadID, {
        revalidateOnFocus: false,
        shouldRetryOnError: false,
        keepPreviousData: false
    })

    return (
        <div>
            <Flex direction='column' gap='0' className='w-full h-[100vh] border-l border-gray-4 sm:dark:border-gray-6'>
                <ThreadHeader />
                {isLoading && <FullPageLoader />}
                {error && <Box p='4'><ErrorBanner error={error} /></Box>}
                {data && <ThreadMessages threadMessage={data} key={threadID} />}
            </Flex>
        </div>
    )
}

export const Component = ThreadDrawer