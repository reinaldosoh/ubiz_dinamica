
import type { DefineComponent, SlotsType } from 'vue'
type IslandComponent<T> = DefineComponent<{}, {refresh: () => Promise<void>}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, SlotsType<{ fallback: { error: unknown } }>> & T

type HydrationStrategies = {
  hydrateOnVisible?: IntersectionObserverInit | true
  hydrateOnIdle?: number | true
  hydrateOnInteraction?: keyof HTMLElementEventMap | Array<keyof HTMLElementEventMap> | true
  hydrateOnMediaQuery?: string
  hydrateAfter?: number
  hydrateWhen?: boolean
  hydrateNever?: true
}
type LazyComponent<T> = DefineComponent<HydrationStrategies, {}, {}, {}, {}, {}, {}, { hydrated: () => void }> & T

interface _GlobalComponents {
  'UAvatar': typeof import("../../components/ui/UAvatar.vue").default
  'UBadge': typeof import("../../components/ui/UBadge.vue").default
  'UButton': typeof import("../../components/ui/UButton.vue").default
  'UCard': typeof import("../../components/ui/UCard.vue").default
  'UDivider': typeof import("../../components/ui/UDivider.vue").default
  'UStatCard': typeof import("../../components/ui/UStatCard.vue").default
  'UTable': typeof import("../../components/ui/UTable.vue").default
  'UTabs': typeof import("../../components/ui/UTabs.vue").default
  'UCheckbox': typeof import("../../components/forms/UCheckbox.vue").default
  'UFileUpload': typeof import("../../components/forms/UFileUpload.vue").default
  'UInput': typeof import("../../components/forms/UInput.vue").default
  'UInputMoney': typeof import("../../components/forms/UInputMoney.vue").default
  'USearchInput': typeof import("../../components/forms/USearchInput.vue").default
  'USelect': typeof import("../../components/forms/USelect.vue").default
  'UTextarea': typeof import("../../components/forms/UTextarea.vue").default
  'UInfoCard': typeof import("../../components/feedback/UInfoCard.vue").default
  'UModal': typeof import("../../components/feedback/UModal.vue").default
  'USteps': typeof import("../../components/feedback/USteps.vue").default
  'USuccessModal': typeof import("../../components/feedback/USuccessModal.vue").default
  'UHeader': typeof import("../../components/layout/UHeader.vue").default
  'UPageTitle': typeof import("../../components/layout/UPageTitle.vue").default
  'UQuickAction': typeof import("../../components/layout/UQuickAction.vue").default
  'AlertModal': typeof import("../../components/AlertModal.vue").default
  'GlobalAlert': typeof import("../../components/GlobalAlert.vue").default
  'MapaPins': typeof import("../../components/MapaPins.client.vue").default
  'SearchableSelect': typeof import("../../components/SearchableSelect.vue").default
  'NuxtWelcome': typeof import("../../node_modules/nuxt/dist/app/components/welcome.vue").default
  'NuxtLayout': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-layout").default
  'NuxtErrorBoundary': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-error-boundary.vue").default
  'ClientOnly': typeof import("../../node_modules/nuxt/dist/app/components/client-only").default
  'DevOnly': typeof import("../../node_modules/nuxt/dist/app/components/dev-only").default
  'ServerPlaceholder': typeof import("../../node_modules/nuxt/dist/app/components/server-placeholder").default
  'NuxtLink': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-link").default
  'NuxtLoadingIndicator': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-loading-indicator").default
  'NuxtTime': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-time.vue").default
  'NuxtRouteAnnouncer': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-route-announcer").default
  'NuxtImg': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtImg
  'NuxtPicture': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtPicture
  'NuxtPage': typeof import("../../node_modules/nuxt/dist/pages/runtime/page").default
  'NoScript': typeof import("../../node_modules/nuxt/dist/head/runtime/components").NoScript
  'Link': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Link
  'Base': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Base
  'Title': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Title
  'Meta': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Meta
  'Style': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Style
  'Head': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Head
  'Html': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Html
  'Body': typeof import("../../node_modules/nuxt/dist/head/runtime/components").Body
  'NuxtIsland': typeof import("../../node_modules/nuxt/dist/app/components/nuxt-island").default
  'LazyUAvatar': LazyComponent<typeof import("../../components/ui/UAvatar.vue").default>
  'LazyUBadge': LazyComponent<typeof import("../../components/ui/UBadge.vue").default>
  'LazyUButton': LazyComponent<typeof import("../../components/ui/UButton.vue").default>
  'LazyUCard': LazyComponent<typeof import("../../components/ui/UCard.vue").default>
  'LazyUDivider': LazyComponent<typeof import("../../components/ui/UDivider.vue").default>
  'LazyUStatCard': LazyComponent<typeof import("../../components/ui/UStatCard.vue").default>
  'LazyUTable': LazyComponent<typeof import("../../components/ui/UTable.vue").default>
  'LazyUTabs': LazyComponent<typeof import("../../components/ui/UTabs.vue").default>
  'LazyUCheckbox': LazyComponent<typeof import("../../components/forms/UCheckbox.vue").default>
  'LazyUFileUpload': LazyComponent<typeof import("../../components/forms/UFileUpload.vue").default>
  'LazyUInput': LazyComponent<typeof import("../../components/forms/UInput.vue").default>
  'LazyUInputMoney': LazyComponent<typeof import("../../components/forms/UInputMoney.vue").default>
  'LazyUSearchInput': LazyComponent<typeof import("../../components/forms/USearchInput.vue").default>
  'LazyUSelect': LazyComponent<typeof import("../../components/forms/USelect.vue").default>
  'LazyUTextarea': LazyComponent<typeof import("../../components/forms/UTextarea.vue").default>
  'LazyUInfoCard': LazyComponent<typeof import("../../components/feedback/UInfoCard.vue").default>
  'LazyUModal': LazyComponent<typeof import("../../components/feedback/UModal.vue").default>
  'LazyUSteps': LazyComponent<typeof import("../../components/feedback/USteps.vue").default>
  'LazyUSuccessModal': LazyComponent<typeof import("../../components/feedback/USuccessModal.vue").default>
  'LazyUHeader': LazyComponent<typeof import("../../components/layout/UHeader.vue").default>
  'LazyUPageTitle': LazyComponent<typeof import("../../components/layout/UPageTitle.vue").default>
  'LazyUQuickAction': LazyComponent<typeof import("../../components/layout/UQuickAction.vue").default>
  'LazyAlertModal': LazyComponent<typeof import("../../components/AlertModal.vue").default>
  'LazyGlobalAlert': LazyComponent<typeof import("../../components/GlobalAlert.vue").default>
  'LazyMapaPins': LazyComponent<typeof import("../../components/MapaPins.client.vue").default>
  'LazySearchableSelect': LazyComponent<typeof import("../../components/SearchableSelect.vue").default>
  'LazyNuxtWelcome': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/welcome.vue").default>
  'LazyNuxtLayout': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-layout").default>
  'LazyNuxtErrorBoundary': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-error-boundary.vue").default>
  'LazyClientOnly': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/client-only").default>
  'LazyDevOnly': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/dev-only").default>
  'LazyServerPlaceholder': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/server-placeholder").default>
  'LazyNuxtLink': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-link").default>
  'LazyNuxtLoadingIndicator': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-loading-indicator").default>
  'LazyNuxtTime': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-time.vue").default>
  'LazyNuxtRouteAnnouncer': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-route-announcer").default>
  'LazyNuxtImg': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtImg>
  'LazyNuxtPicture': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtPicture>
  'LazyNuxtPage': LazyComponent<typeof import("../../node_modules/nuxt/dist/pages/runtime/page").default>
  'LazyNoScript': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").NoScript>
  'LazyLink': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Link>
  'LazyBase': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Base>
  'LazyTitle': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Title>
  'LazyMeta': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Meta>
  'LazyStyle': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Style>
  'LazyHead': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Head>
  'LazyHtml': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Html>
  'LazyBody': LazyComponent<typeof import("../../node_modules/nuxt/dist/head/runtime/components").Body>
  'LazyNuxtIsland': LazyComponent<typeof import("../../node_modules/nuxt/dist/app/components/nuxt-island").default>
}

declare module 'vue' {
  export interface GlobalComponents extends _GlobalComponents { }
}

export {}
