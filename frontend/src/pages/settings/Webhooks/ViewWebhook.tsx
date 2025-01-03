import { ErrorBanner } from "@/components/layout/AlertBanner/ErrorBanner"
import { FullPageLoader } from "@/components/layout/Loaders/FullPageLoader"
import { useDontManageGetDoc } from "dontmanage-react-sdk"
import { useParams } from "react-router-dom"
import { RavenWebhook } from "@/types/RavenIntegrations/RavenWebhook"
import { ViewWebhookPage } from "@/components/feature/integrations/webhooks/ViewWebhookPage"
import PageContainer from "@/components/layout/Settings/PageContainer"

const ViewWebhook = () => {

    const { ID } = useParams<{ ID: string }>()
    const { data, error, isLoading, mutate } = useDontManageGetDoc<RavenWebhook>('Raven Webhook', ID, undefined, {
        shouldRetryOnError: false,
    })

    return (
        <PageContainer>
            {isLoading && <FullPageLoader className="h-64" />}
            {error && <ErrorBanner error={error} />}
            {data && <ViewWebhookPage data={data} mutate={mutate} />}

        </PageContainer>
    )
}

export const Component = ViewWebhook