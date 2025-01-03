import { BiInfoCircle } from "react-icons/bi"
import { Link as RadixLink, Text } from "@radix-ui/themes"
import { CustomCallout } from "@/components/common/Callouts/CustomCallout"
import { useDontManageGetCall } from "frappe-react-sdk"

const ServerScriptNotEnabledCallout = () => {

    const { data } = useDontManageGetCall("dontmanage.core.doctype.server_script.server_script.enabled", undefined, undefined, {
        revalidateIfStale: false,
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    })

    if (data?.message) {
        return null
    }

    return (
        <CustomCallout
            iconChildren={<BiInfoCircle size='18' />}
            rootProps={{ color: 'yellow', variant: 'surface' }}
            textChildren={<Text>Server scripts are not enabled on this site. Please view the <RadixLink target="_blank" href="https://dontmanageframework.com/docs/user/en/desk/scripting/server-script" color='yellow' underline='always'>DontManage documentation</RadixLink> for more information.</Text>}
        />
    )
}

export default ServerScriptNotEnabledCallout