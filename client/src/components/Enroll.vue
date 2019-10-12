<template>
  <el-container>
    <el-header>
      <el-row>
        <el-col>
          <h1>声纹识别系统 v0.0.1</h1>
        </el-col>
      </el-row>
    </el-header>
    <el-main>
      <el-col>
        <div class="grid-content bg-purple-light">
          <el-tabs v-model="activeTab" type="border-card" @tab-click="handleClick">
            <el-tab-pane label="注册" name="enroll">
              <el-form ref="form" label-width="20%">
                <el-steps :active="enrollStep" align-center finish-status="success">
                  <el-step title="填写信息" description="输入新说话人姓名或选择一说话人。"></el-step>
                  <el-step title="录音" description="点击录音，完毕后点击停止结束录音，点击播放可以试听。"></el-step>
                  <el-step title="上传" description="点击保存按钮将录音上传至云端。"></el-step>
                </el-steps>
                <br>
                <el-form-item label="新说话人名称">
                  <el-input v-model="name"></el-input>
                </el-form-item>
                <el-form-item label="已存在说话人">
                  <el-select v-model="value" placeholder="请选择" @focus="get_options">
                    <el-option
                      v-for="item in options"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                    </el-option>
                  </el-select>
                </el-form-item>
                <vue-dictaphone-spectrum-analyser style="height: 200px; width: 100%; margin-left: 20px;"/>
                <template v-if="audioSource">
                  <audio :src="audioSource" controls></audio>
                </template>
                <vue-dictaphone @stop="handleRecording($event)" mime-type="audio/wav">
                  <template slot-scope="{ isRecording, startRecording, stopRecording, deleteRecording }">
                    <el-button type="primary" style="margin-left: 20px" v-if="!isRecording" @click="startRecording">录音</el-button>
                    <el-button type="danger" style="margin-left: 20px" v-else @click="stopRecording">停止</el-button>
                    <el-button type="success" v-if="audioSource" @click="uploadEnroll">上传</el-button>
                  </template>
                </vue-dictaphone>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="测试" name="test">
              <el-steps v-bind:active="testStep" align-center finish-status="success">
                <el-step title="录音" description="点击录音，完毕后点击停止结束录音，点击播放可以试听。"></el-step>
                <el-step title="上传" description="点击保存按钮将录音上传至云端。"></el-step>
              </el-steps>
              <vue-dictaphone-spectrum-analyser style="height: 200px; width: 100%; margin-left: 20px;"/>
              <template v-if="audioSource">
                <audio :src="audioSource" controls></audio>
              </template>
              <vue-dictaphone @stop="handleRecording($event)">
                <template slot-scope="{ isRecording, startRecording, stopRecording }">
                  <el-button type="primary" style="margin-left: 20px" v-if="!isRecording" @click="startRecording">录音</el-button>
                  <el-button type="danger" style="margin-left: 20px" v-else @click="stopRecording">停止</el-button>
                  <el-button type="success" v-if="audioSource" @click="uploadTest">上传</el-button>
                </template>
              </vue-dictaphone>
            </el-tab-pane>
            <el-tab-pane label="检查" name="check">
              <el-table
                v-loading="loading"
                :data="tableData.filter(data => !speaker_table_search || data.name.toLowerCase().includes(speaker_table_search.toLowerCase()))"
                style="width: 100%" max-height="250">
                <el-table-column align="center" prop="date" label="添加日期" :min-width="23" sortable></el-table-column>
                <el-table-column align="center" prop="name" label="说话人姓名" :min-width="22"></el-table-column>
                <el-table-column align="center" prop="number" label="已注册语句" :min-width="20" sortable></el-table-column>
                <el-table-column align="right" :min-width="35">
                  <template slot="header" slot-scope="scope">
                    <!-- why we need slot-scope to activate input box? -->
                    <el-input
                      v-model="speaker_table_search"
                      size="mini"
                      placeholder="输入姓名搜索"/>
                  </template>
                  <template slot-scope="scope">
                    <el-button
                      size="mini"
                      type="danger"
                      @click="handleDelete(scope.row.name)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-main>
  </el-container>
</template>

<style>
  svg{
    vertical-align: top;
  }

  .ar-icon{
    border: 1px solid #409EFF!important;
  }

  .el-form-item__content .ar-recorder__duration{
    margin-top: 30px!important;
  }
  hint{
    text-decoration: underline;
    color: #AEAEAE;
  }
</style>

<script>/* eslint-disable indent, quotes, max-len */
  import axios from 'axios';

  export default {
    data() {
      return {
        name: '',
        value: '',
        loading: true,
        enroll_sended: 0,
        enroll_recorded: 0,
        test_sended: 0,
        test_recorded: 0,
        tableData: [],
        activeTab: "enroll",
        options: [],
        audioSource: null,
        speaker_table_search: '',
      };
    },
    methods: {
      get_options() {
        const vm = this;
        axios({
          url: 'https://vzxxbacq.cn/server/options',
          method: 'get',
          value: '',
          timeout: 5000,
          headers: {
            'Content-Type': 'application/json',
          },
        }).then((res) => {
          console.log(res);
          console.log(res.data);
          console.log(vm.options);
          vm.options = res.data;
        });
      },
      handleClick(tab, event) {
        this.audioSource = null;
        this.enroll_sended = 0;
        this.test_sended = 0;
        if (tab.paneName === 'check') {
          const vm = this;
          vm.loading = true;
          vm.test_sended = 0;
          vm.test_recorded = 0;
          vm.enroll_sended = 0;
          vm.enroll_recorded = 0;
          const tableDataPath = "https://vzxxbacq.cn/server/spkr_list";
          axios({
            url: tableDataPath,
            method: 'post',
          }).then((res) => {
            if (res.data.table) {
              vm.tableData = res.data.table;
            }
            vm.loading = false;
          }).catch((error) => {
            vm.$alert(error, '错误', {
              comfirmButtomText: "OK",
            });
            vm.loading = false;
          });
        }
      },
      uploadEnroll() {
        console.log("Call Upload Enroll");
        const path = "https://vzxxbacq.cn/server/upload_enroll";
        const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)',
        });
        setTimeout(() => {
          loading.close();
        }, 2000);
        let postName = "";
        if (this.value !== null && this.value !== '' && this.value !== undefined) {
          postName = this.value;
        } else if (this.name !== null && this.name !== '' && this.name !== undefined) {
          postName = this.name;
        } else {
          this.$alert('请输入说话人姓名或者选择已有说话人', "错误", {
            confirmButtonText: "OK",
          });
          return;
        }
        fetch(this.audioSource).then(
          r => r.blob(),
        ).then(
          blobFile => new File([blobFile], "upload.wav"),
        ).then(
          (file) => {
            console.log(file);
            this.enroll_sended += 1;
            const data = new FormData();
            data.append('file', file);
            data.append('name', postName);
            data.append('type', 'enroll');
            const config = {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            };
            axios.post(path, data, config).then((res) => {
              this.$alert(res.data.msg, "来自服务端的消息", {
                confirmButtonText: "好的",
              });
              loading.close();
            }).catch((e) => {
              this.$alert(e, "错误", {
                confirmButtonText: "OK",
              });
            });
          },
        );
      },
      uploadTest() {
        console.log("Call Upload Test");
        console.log(this.audioSource);
        const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)',
        });
        setTimeout(() => {
          loading.close();
        }, 2000);
        const path = "https://vzxxbacq.cn/server/test_upload";
        fetch(this.audioSource).then(
          r => r.blob(),
        ).then(
          blobFile => new File([blobFile], "upload.wav"),
        ).then(
          (file) => {
            console.log(file);
            this.test_sended += 1;
            const data = new FormData();
            data.append('file', file);
            data.append('type', 'test');
            const config = {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            };
            axios.post(path, data, config).then((res) => {
              this.$alert(res.data.msg, "来自服务端的消息", {
                confirmButtonText: "好的",
              });
              loading.close();
            }).catch((e) => {
              this.$alert(e, "错误", {
                confirmButtonText: "OK",
              });
            });
          },
        );
      },
      handleDelete(name) {
        axios({
          url: "https://vzxxbacq.cn/server/delete",
          data: {
            name,
          },
          method: 'post',
        });
      },
      handleError() {
        this.showError = true;
      },
      // eslint-disable-next-line no-unused-vars
      handleRecording({ blob, src }) {
        this.audioSource = src;
      },
    },
    computed: {
      testStep() {
        if (!this.audioSource) {
          return 0;
        }
        if (this.test_sended !== 0) {
          return 1;
        }
        return 2;
      },
      enrollStep() {
        if (!this.value && !this.name) {
          return 0;
        }
        if (!this.audioSource) {
          return 1;
        }
        if (this.enroll_sended !== 0) {
          return 3;
        }
        return 2;
      },
    },
  };
</script>
