<script setup lang="ts">
import VesselScene from './components/VesselScene.vue';defineProps<{svg:string;vessel:string}>();
</script><template><VesselScene :svg="svg" :vessel="vessel"/></template>
