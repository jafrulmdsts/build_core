<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();
locale.value = 'bn';
</script>

<template>
  <RouterView />
</template>
