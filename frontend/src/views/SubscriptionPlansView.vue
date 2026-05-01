<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { Crown, Check, Loader2 } from '@lucide/vue';
import api from '@/lib/api';

const { locale } = useI18n();
const isBangla = computed(() => locale.value === 'bn');

interface Plan {
  id: string;
  name: string;
  slug: string;
  price_monthly: number;
  price_yearly: number;
  max_users: number;
  max_projects: number;
  features: string[];
  is_active: boolean;
}

const plans = ref<Plan[]>([]);
const loading = ref(true);

async function fetchPlans() {
  loading.value = true;
  try {
    const { data } = await api.get('/subscriptions');
    plans.value = (data.data || []).filter((p: Plan) => p.is_active);
  } catch { plans.value = []; } finally { loading.value = false; }
}

function formatPrice(price: number) {
  if (price === 0) return isBangla.value ? 'বিনামূল্য' : 'Free';
  return `৳${price.toLocaleString()}`;
}

const planAccents = ['border-emerald-500 ring-emerald-500', 'border-blue-500 ring-blue-500', 'border-purple-500 ring-purple-500'];

onMounted(fetchPlans);
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-slate-900">{{ isBangla ? 'সাবস্ক্রিপশন প্ল্যান' : 'Subscription Plans' }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ isBangla ? 'আপনার প্রয়োজন অনুযায়ী প্ল্যান বেছে নিন' : 'Choose the plan that fits your needs' }}</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-600" />
    </div>

    <!-- Empty -->
    <div v-else-if="plans.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Crown :size="48" class="text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-900">{{ isBangla ? 'কোন প্ল্যান নেই' : 'No Plans Available' }}</h3>
    </div>

    <!-- Plan Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="(plan, idx) in plans" :key="plan.id"
        :class="['rounded-xl border-2 bg-white shadow-sm p-6 flex flex-col transition-shadow hover:shadow-md', planAccents[idx % planAccents.length]]">
        <!-- Plan Header -->
        <div class="mb-6">
          <h3 class="text-lg font-bold text-slate-900">{{ plan.name }}</h3>
          <div class="mt-3 flex items-baseline gap-1">
            <span class="text-3xl font-bold text-slate-900">{{ formatPrice(plan.price_monthly) }}</span>
            <span v-if="plan.price_monthly > 0" class="text-sm text-slate-500">/ {{ isBangla ? 'মাসিক' : 'mo' }}</span>
          </div>
          <p v-if="plan.price_yearly > 0 && plan.price_monthly > 0" class="mt-1 text-xs text-emerald-600 font-medium">
            {{ isBangla ? 'বার্ষিক' : 'Yearly' }}: ৳{{ plan.price_yearly.toLocaleString() }}
          </p>
        </div>

        <!-- Limits -->
        <div class="flex gap-4 mb-6">
          <div class="flex items-center gap-1.5 text-sm text-slate-600">
            <span class="font-semibold text-slate-900">{{ plan.max_users }}</span>
            {{ isBangla ? 'ব্যবহারকারী' : 'Users' }}
          </div>
          <div class="flex items-center gap-1.5 text-sm text-slate-600">
            <span class="font-semibold text-slate-900">{{ plan.max_projects }}</span>
            {{ isBangla ? 'প্রকল্প' : 'Projects' }}
          </div>
        </div>

        <!-- Features -->
        <ul class="space-y-2.5 flex-1 mb-6">
          <li v-for="feature in plan.features" :key="feature" class="flex items-start gap-2 text-sm text-slate-600">
            <Check :size="16" class="text-emerald-500 flex-shrink-0 mt-0.5" />
            <span>{{ feature }}</span>
          </li>
        </ul>

        <!-- CTA -->
        <button class="w-full rounded-lg py-2.5 text-sm font-semibold transition-colors cursor-pointer"
          :class="plan.price_monthly === 0 ? 'bg-slate-100 text-slate-700 hover:bg-slate-200' : 'bg-emerald-600 text-white hover:bg-emerald-700'">
          {{ plan.price_monthly === 0 ? (isBangla ? 'বর্তমান প্ল্যান' : 'Current Plan') : (isBangla ? 'আপগ্রেড করুন' : 'Upgrade') }}
        </button>
      </div>
    </div>
  </div>
</template>
