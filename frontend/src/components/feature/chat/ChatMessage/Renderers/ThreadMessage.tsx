import { Link, useParams } from "react-router-dom"
import { Message } from "../../../../../../../types/Messaging/Message"
import { Button, Flex, Text } from "@radix-ui/themes"
import { useDontManageGetDocCount } from "dontmanage-react-sdk"
import { RavenMessage } from "@/types/RavenMessaging/RavenMessage"
import { useDontManageDocumentEventListener } from "dontmanage-react-sdk"
import { useDontManageEventListener } from "dontmanage-react-sdk"

export const ThreadMessage = ({ thread }: { thread: Message }) => {

    const { workspaceID } = useParams()

    return (
        <div className="mt-2">
            <Flex justify={'between'} align={'center'} gap='2' className="w-fit px-3 py-2 border border-gray-4 rounded-md shadow-[0_20px_30px_-10px_rgba(0,0,0,0.1)]">
                <ThreadReplyCount thread={thread} />
                <Button size={'1'}
                    asChild
                    color="gray"
                    variant={'ghost'}
                    className={'not-cal w-fit hover:bg-transparent hover:underline cursor-pointer'}>
                    <Link to={`/${workspaceID}/${thread.channel_id}/thread/${thread.name}`}>View Thread</Link>
                </Button>
            </Flex>
        </div>
    )
}

export const ThreadReplyCount = ({ thread }: { thread: Message }) => {

    const { data, mutate } = useDontManageGetDocCount<RavenMessage>("Raven Message", [["channel_id", "=", thread.name]], undefined, undefined, undefined, {
        revalidateOnFocus: false,
        shouldRetryOnError: false,
        keepPreviousData: false
    })

    // Listen to realtime event for new message count
    useDontManageDocumentEventListener('Raven Message', thread.name, () => { })

    useDontManageEventListener('thread_reply_created', () => {
        mutate()
    })

    return <Flex gap='1' align={'center'}>
        <Text size='1' className={'font-semibold text-accent-a11'}>{data ?? 0}</Text>
        <Text size='1' className={'font-semibold text-accent-a11'}>{data && data === 1 ? 'Reply' : 'Replies'}</Text>
    </Flex>
}