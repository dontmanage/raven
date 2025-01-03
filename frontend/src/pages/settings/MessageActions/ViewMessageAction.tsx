import { Loader } from "@/components/common/Loader"
import MessageActionForm from "@/components/feature/message-actions/MessageActionForm"
import { ErrorBanner } from "@/components/layout/AlertBanner/ErrorBanner"
import { FullPageLoader } from "@/components/layout/Loaders/FullPageLoader"
import PageContainer from "@/components/layout/Settings/PageContainer"
import SettingsContentContainer from "@/components/layout/Settings/SettingsContentContainer"
import SettingsPageHeader from "@/components/layout/Settings/SettingsPageHeader"
import { HStack } from "@/components/layout/Stack"
import { RavenMessageAction } from "@/types/RavenIntegrations/RavenMessageAction"
import { isEmpty } from "@/utils/validations"
import { Button } from "@radix-ui/themes"
import { useDontManageGetDoc, useDontManageUpdateDoc, SWRResponse } from "dontmanage-react-sdk"
import { useEffect } from "react"
import { FormProvider, useForm } from "react-hook-form"
import { useParams } from "react-router-dom"
import { toast } from "sonner"

type Props = {}

const ViewMessageAction = (props: Props) => {

    const { ID } = useParams<{ ID: string }>()

    const { data, isLoading, error, mutate } = useDontManageGetDoc<RavenMessageAction>("Raven Message Action", ID)

    return (
        <PageContainer>
            <ErrorBanner error={error} />
            {isLoading && <FullPageLoader className="h-64" />}
            {data && <ViewMessageActionContent data={data} mutate={mutate} />}
        </PageContainer>
    )
}

const ViewMessageActionContent = ({ data, mutate }: { data: RavenMessageAction, mutate: SWRResponse['mutate'] }) => {

    const { updateDoc, loading, error } = useDontManageUpdateDoc<RavenMessageAction>()

    const methods = useForm<RavenMessageAction>({
        disabled: loading,
        defaultValues: data
    })

    const { formState: { dirtyFields } } = methods

    const isDirty = !isEmpty(dirtyFields)


    const onSubmit = (data: RavenMessageAction) => {
        updateDoc("Raven Message Action", data.name, data)
            .then((doc) => {
                toast.success("Saved")
                methods.reset(doc)
                mutate(doc, { revalidate: false })
            })
    }

    useEffect(() => {

        const down = (e: KeyboardEvent) => {
            if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                methods.handleSubmit(onSubmit)()
            }
        }

        document.addEventListener('keydown', down)
        return () => document.removeEventListener('keydown', down)
    }, [])



    return <form onSubmit={methods.handleSubmit(onSubmit)}>
        <FormProvider {...methods}>
            <SettingsContentContainer>
                <SettingsPageHeader
                    title={data.action_name}
                    headerBadges={isDirty ? [{ label: "Not Saved", color: "red" }] : undefined}
                    actions={<HStack>
                        <Button type='submit' disabled={loading}>
                            {loading && <Loader className="text-white" />}
                            {loading ? "Saving" : "Save"}
                        </Button>
                    </HStack>}
                    breadcrumbs={[{ label: 'Message Actions', href: '../' }, { label: data.action_name, href: '', copyToClipboard: true }]}
                />
                <ErrorBanner error={error} />
                <MessageActionForm />
            </SettingsContentContainer>
        </FormProvider>
    </form>

}

export const Component = ViewMessageAction