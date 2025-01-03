import { useDontManageGetCall } from "dontmanage-react-sdk"

/**
 * Simple hook to show Doctype preview data
 * @returns name(id), preview_image, preview_title and rest fields depending on Doctype
 */
export const useDoctypePreview = (doctype: string, docname: string) => {
    const { data, error, isLoading, mutate } = useDontManageGetCall('raven.api.document_link.get_preview_data', {
        doctype,
        docname
    }, undefined, {
        shouldRetryOnError: false
    })

    return {
        data: data?.message,
        error,
        isLoading,
        mutate
    }
}