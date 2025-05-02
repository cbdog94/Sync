<template>
  <el-row>
    <el-col v-loading="loading" :offset="2" :span="20">
      <h4>同步文本</h4>
      <el-input
        v-show="syncData.show"
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 10 }"
        placeholder="请输入需要同步的文本"
        v-model="syncData.text"
      ></el-input>
      <el-checkbox
        v-show="syncData.show"
        class="topmargin"
        v-model="syncData.once"
        >阅后即焚</el-checkbox
      >
      <p v-show="!syncData.show">
        提取码:
        <span style="color: #f56c6c; font-size: 18px">{{ syncData.code }}</span>
      </p>
    </el-col>
    <el-col :span="24">
      <el-button
        v-show="syncData.show"
        class="topmargin"
        type="primary"
        plain
        size="large"
        @click="sync"
        >同步</el-button
      >
      <el-button
        v-show="!syncData.show"
        class="topmargin"
        type="primary"
        size="large"
        plain
        @click="backsync"
        >再次同步</el-button
      >
    </el-col>
  </el-row>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      syncData: {
        text: "",
        once: false,
        show: true,
        code: "",
      },
    };
  },
  methods: {
    sync() {
      var _self = this;
      if (_self.syncData.text == "") {
        _self.$message({
          message: "请输入需要同步的文本！",
          type: "warning",
        });
        return;
      }
      _self.loading = true;
      this.axios
        .post("/syncbackend/submit", {
          text: _self.syncData.text,
          once: _self.syncData.once,
        })
        .then(function (response) {
          if (response.data.code != 0) {
            _self.loading = false;
            _self.$message.error("同步失败!");
            console.log(response);
            return;
          }
          _self.loading = false;
          _self.syncData.code = response.data.result.code;
          _self.syncData.show = false;
          _self.$message({
            message: "同步成功，请记录提取码！",
            type: "success",
          });
        })
        .catch(function (error) {
          _self.loading = false;
          console.log(error);
          _self.$message.error("同步失败!");
        });
    },
    backsync() {
      this.syncData.show = true;
      this.syncData.once = false;
      this.syncData.text = "";
      this.syncData.code = "";
    },
  },
};
</script>

<style>
h4 {
  color: #303133;
}
.topmargin {
  margin-top: 20px;
}
p {
  color: #303133;
}
</style>
