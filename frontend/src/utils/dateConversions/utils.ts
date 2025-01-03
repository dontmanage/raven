import * as dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import advancedFormat from 'dayjs/plugin/advancedFormat'

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(advancedFormat)

const DEFAULT_TIME_ZONE = 'Asia/Kolkata'
//@ts-expect-error
export const SYSTEM_TIMEZONE = window.dontmanage?.boot?.time_zone?.system || DEFAULT_TIME_ZONE

//@ts-expect-error
export const USER_DATE_FORMAT = (window.dontmanage?.boot?.user?.defaults?.date_format?.toUpperCase() || window.dontmanage?.boot?.sysdefaults?.date_format?.toUpperCase()
    || 'DD/MM/YYYY')

export const DONTMANAGE_DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
export const DONTMANAGE_DATE_FORMAT = 'YYYY-MM-DD'
export const DONTMANAGE_TIME_FORMAT = 'HH:mm:ss'

export const getDateObject = (timestamp: string): dayjs.Dayjs => {

    return dayjs.tz(timestamp, SYSTEM_TIMEZONE).local()
}

export const convertMillisecondsToReadableDate = (timestampInMilliseconds: number, format: string = 'hh:mm A (Do MMM)') => {

    return dayjs.unix(timestampInMilliseconds / 1000)
}