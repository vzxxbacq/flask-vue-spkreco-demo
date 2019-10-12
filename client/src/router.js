import Vue from 'vue';
import AudioRecorder from 'vue-audio-recorder';
import Router from 'vue-router';
import Ping from './components/Ping.vue';
import Enroll from './components/Enroll.vue';

Vue.use(Router);
Vue.use(AudioRecorder);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
    {
      path: '/',
      name: 'Enroll',
      component: Enroll,
    },
  ],
});
