import { RavenSettings } from "@/types/Raven/RavenSettings"
import { useDontManageGetDoc } from "dontmanage-react-sdk"

const useRavenSettings = () => {

    const { data, mutate } = useDontManageGetDoc<RavenSettings>("Raven Settings", "Raven Settings", "raven_settings", {
        revalidateOnFocus: false,
        // Refresh every 8 hours or on page refresh
        dedupingInterval: 8 * 60 * 60 * 1000
    })

    return {
        ravenSettings: data,
        mutate
    }
}

export default useRavenSettings