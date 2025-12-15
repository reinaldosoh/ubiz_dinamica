
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


export const UAvatar: typeof import("../components/ui/UAvatar.vue").default
export const UBadge: typeof import("../components/ui/UBadge.vue").default
export const UButton: typeof import("../components/ui/UButton.vue").default
export const UCard: typeof import("../components/ui/UCard.vue").default
export const UDivider: typeof import("../components/ui/UDivider.vue").default
export const UStatCard: typeof import("../components/ui/UStatCard.vue").default
export const UTable: typeof import("../components/ui/UTable.vue").default
export const UTabs: typeof import("../components/ui/UTabs.vue").default
export const UCheckbox: typeof import("../components/forms/UCheckbox.vue").default
export const UFileUpload: typeof import("../components/forms/UFileUpload.vue").default
export const UInput: typeof import("../components/forms/UInput.vue").default
export const UInputMoney: typeof import("../components/forms/UInputMoney.vue").default
export const USearchInput: typeof import("../components/forms/USearchInput.vue").default
export const USelect: typeof import("../components/forms/USelect.vue").default
export const UTextarea: typeof import("../components/forms/UTextarea.vue").default
export const UInfoCard: typeof import("../components/feedback/UInfoCard.vue").default
export const UModal: typeof import("../components/feedback/UModal.vue").default
export const USteps: typeof import("../components/feedback/USteps.vue").default
export const USuccessModal: typeof import("../components/feedback/USuccessModal.vue").default
export const UHeader: typeof import("../components/layout/UHeader.vue").default
export const UPageTitle: typeof import("../components/layout/UPageTitle.vue").default
export const UQuickAction: typeof import("../components/layout/UQuickAction.vue").default
export const AlertModal: typeof import("../components/AlertModal.vue").default
export const GlobalAlert: typeof import("../components/GlobalAlert.vue").default
export const MapaPins: typeof import("../components/MapaPins.client.vue").default
export const SearchableSelect: typeof import("../components/SearchableSelect.vue").default
export const NuxtWelcome: typeof import("../node_modules/nuxt/dist/app/components/welcome.vue").default
export const NuxtLayout: typeof import("../node_modules/nuxt/dist/app/components/nuxt-layout").default
export const NuxtErrorBoundary: typeof import("../node_modules/nuxt/dist/app/components/nuxt-error-boundary.vue").default
export const ClientOnly: typeof import("../node_modules/nuxt/dist/app/components/client-only").default
export const DevOnly: typeof import("../node_modules/nuxt/dist/app/components/dev-only").default
export const ServerPlaceholder: typeof import("../node_modules/nuxt/dist/app/components/server-placeholder").default
export const NuxtLink: typeof import("../node_modules/nuxt/dist/app/components/nuxt-link").default
export const NuxtLoadingIndicator: typeof import("../node_modules/nuxt/dist/app/components/nuxt-loading-indicator").default
export const NuxtTime: typeof import("../node_modules/nuxt/dist/app/components/nuxt-time.vue").default
export const NuxtRouteAnnouncer: typeof import("../node_modules/nuxt/dist/app/components/nuxt-route-announcer").default
export const NuxtImg: typeof import("../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtImg
export const NuxtPicture: typeof import("../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtPicture
export const NuxtPage: typeof import("../node_modules/nuxt/dist/pages/runtime/page").default
export const NoScript: typeof import("../node_modules/nuxt/dist/head/runtime/components").NoScript
export const Link: typeof import("../node_modules/nuxt/dist/head/runtime/components").Link
export const Base: typeof import("../node_modules/nuxt/dist/head/runtime/components").Base
export const Title: typeof import("../node_modules/nuxt/dist/head/runtime/components").Title
export const Meta: typeof import("../node_modules/nuxt/dist/head/runtime/components").Meta
export const Style: typeof import("../node_modules/nuxt/dist/head/runtime/components").Style
export const Head: typeof import("../node_modules/nuxt/dist/head/runtime/components").Head
export const Html: typeof import("../node_modules/nuxt/dist/head/runtime/components").Html
export const Body: typeof import("../node_modules/nuxt/dist/head/runtime/components").Body
export const NuxtIsland: typeof import("../node_modules/nuxt/dist/app/components/nuxt-island").default
export const LazyUAvatar: LazyComponent<typeof import("../components/ui/UAvatar.vue").default>
export const LazyUBadge: LazyComponent<typeof import("../components/ui/UBadge.vue").default>
export const LazyUButton: LazyComponent<typeof import("../components/ui/UButton.vue").default>
export const LazyUCard: LazyComponent<typeof import("../components/ui/UCard.vue").default>
export const LazyUDivider: LazyComponent<typeof import("../components/ui/UDivider.vue").default>
export const LazyUStatCard: LazyComponent<typeof import("../components/ui/UStatCard.vue").default>
export const LazyUTable: LazyComponent<typeof import("../components/ui/UTable.vue").default>
export const LazyUTabs: LazyComponent<typeof import("../components/ui/UTabs.vue").default>
export const LazyUCheckbox: LazyComponent<typeof import("../components/forms/UCheckbox.vue").default>
export const LazyUFileUpload: LazyComponent<typeof import("../components/forms/UFileUpload.vue").default>
export const LazyUInput: LazyComponent<typeof import("../components/forms/UInput.vue").default>
export const LazyUInputMoney: LazyComponent<typeof import("../components/forms/UInputMoney.vue").default>
export const LazyUSearchInput: LazyComponent<typeof import("../components/forms/USearchInput.vue").default>
export const LazyUSelect: LazyComponent<typeof import("../components/forms/USelect.vue").default>
export const LazyUTextarea: LazyComponent<typeof import("../components/forms/UTextarea.vue").default>
export const LazyUInfoCard: LazyComponent<typeof import("../components/feedback/UInfoCard.vue").default>
export const LazyUModal: LazyComponent<typeof import("../components/feedback/UModal.vue").default>
export const LazyUSteps: LazyComponent<typeof import("../components/feedback/USteps.vue").default>
export const LazyUSuccessModal: LazyComponent<typeof import("../components/feedback/USuccessModal.vue").default>
export const LazyUHeader: LazyComponent<typeof import("../components/layout/UHeader.vue").default>
export const LazyUPageTitle: LazyComponent<typeof import("../components/layout/UPageTitle.vue").default>
export const LazyUQuickAction: LazyComponent<typeof import("../components/layout/UQuickAction.vue").default>
export const LazyAlertModal: LazyComponent<typeof import("../components/AlertModal.vue").default>
export const LazyGlobalAlert: LazyComponent<typeof import("../components/GlobalAlert.vue").default>
export const LazyMapaPins: LazyComponent<typeof import("../components/MapaPins.client.vue").default>
export const LazySearchableSelect: LazyComponent<typeof import("../components/SearchableSelect.vue").default>
export const LazyNuxtWelcome: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/welcome.vue").default>
export const LazyNuxtLayout: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-layout").default>
export const LazyNuxtErrorBoundary: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-error-boundary.vue").default>
export const LazyClientOnly: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/client-only").default>
export const LazyDevOnly: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/dev-only").default>
export const LazyServerPlaceholder: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/server-placeholder").default>
export const LazyNuxtLink: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-link").default>
export const LazyNuxtLoadingIndicator: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-loading-indicator").default>
export const LazyNuxtTime: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-time.vue").default>
export const LazyNuxtRouteAnnouncer: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-route-announcer").default>
export const LazyNuxtImg: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtImg>
export const LazyNuxtPicture: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-stubs").NuxtPicture>
export const LazyNuxtPage: LazyComponent<typeof import("../node_modules/nuxt/dist/pages/runtime/page").default>
export const LazyNoScript: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").NoScript>
export const LazyLink: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Link>
export const LazyBase: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Base>
export const LazyTitle: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Title>
export const LazyMeta: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Meta>
export const LazyStyle: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Style>
export const LazyHead: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Head>
export const LazyHtml: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Html>
export const LazyBody: LazyComponent<typeof import("../node_modules/nuxt/dist/head/runtime/components").Body>
export const LazyNuxtIsland: LazyComponent<typeof import("../node_modules/nuxt/dist/app/components/nuxt-island").default>

export const componentNames: string[]
