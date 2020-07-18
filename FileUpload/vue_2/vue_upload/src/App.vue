<template>
  <div id="global-uploader">
    <h2>文本校验</h2>
    <uploader
      ref="uploader"
      :options="options"
      :autoStart="false"
      :file-status-text="statusText"
      @file-added="onFileAdded"
      @file-success="onFileSuccess"
      @file-progress="onFileProgress"
      @file-error="onFileError"
      class="uploader-app"
    >
      <uploader-unsupport></uploader-unsupport>
      <uploader-drop>
        <uploader-btn id="global-uploader-btn" :attrs="attrs" ref="uploadBtn">
          <i class="upload-iconfont upload-iconupload"></i> 上传文件
        </uploader-btn>
      </uploader-drop>
      <uploader-list>
        <div class="file-panel" slot-scope="props">
          <!-- <div class="file-title">
            <h3>文件列表</h3>
          </div>-->

          <ul class="file-list">
            <li v-for="file in props.fileList" :key="file.id">
              <uploader-file :class="'file_' + file.id" ref="files" :file="file" :list="true"></uploader-file>
              <div class="query_check" v-if="queryBtnShow">
                <button v-on:click="queryCheck(uuid)">校验查询</button>
                <!-- <input type="button" v-on="queryCheck(uuid)" value="校"/> -->
                <!-- <div v-if="queryCheckStatus">文件正在上传中</div> -->
                <span class="queryCheckShow" v-if="queryCheckShow">{{checkStatus}}</span>
              </div>
              <div class="save-result" v-if="saveBtnShow">
                <button v-on:click="download_check_result(file_path)">校验保存</button>
              </div>
            </li>
            <div class="no-file" v-if="!props.fileList.length">
              <i class="iconfont icon-empty-file"></i> 暂无待上传文件
            </div>
          </ul>
        </div>
      </uploader-list>
    </uploader>
  </div>
</template>

<script>
import $ from "jquery";
import Bus from "./utils/bus.js";
import SparkMD5 from "spark-md5";
import { ACCEPT_CONFIG } from "./utils/config";

export default {
  data() {
    return {
      options: {
        target: "http://127.0.0.1:8000/fileUpload/globalUpload", // 目标上传URL
        testChunks: true,
        chunkSize: "2048000",
        // chunkSize: "10240000", // 分块时按该值来分
        fileParameterName: "file", // 上传文件时文件的参数名
        maxChunkRetries: 3, // 最大自动失败重试上传次数

	// 由于我自身业务原因, 添加了校验查询功能, 查询的时候不能控制
	// 对应上传文件的id, 因此,去掉了多文件上传
	// 这里注释掉, 就可以实现多文件上传了
        singleFile: true, // 单文件上传

        // 上传分片前, 会先向后端发送一个get请求, 该函数就是响应这个get请求
        checkChunkUploadedByResponse: function(chunk, message) {
          let objMessage = JSON.parse(message);
          console.log("objMessage:", objMessage);

	  //---------秒传说明------------
	  // 此处解开注释, 配合后端传来的参数可以实现秒传, 我因为上传后还需要进行校验请求,
	  // 这里我就砍掉秒传功能了..
	  //-----------------------------
          // 此处根据返回值来判断是否为秒传
          // if (objMessage.skipUpload === "true") {
          //   return true;
          // }
          // 根据返回的数组内容来判断哪些分片不需要重新上传
          return (objMessage.uploaded || []).indexOf(chunk.offset + 1) >= 0;
        },
        parseTimeRemaining: function(timeRemaining, parsedTimeRemaining) {
          return parsedTimeRemaining
            .replace(/\syears?/, "年")
            .replace(/\days?/, "天")
            .replace(/\shours?/, "小时")
            .replace(/\sminutes?/, "分钟")
            .replace(/\sseconds?/, "秒");
        }
      },
      attrs: {
        accept: ACCEPT_CONFIG.getAll()
      },
      statusText: {
        success: "文件类型不符, 请重新上传",
        error: "上传出错,请检查网络后重试",
        uploading: "上传中",
        typeError: "暂不支持上传您添加的文件格式",
        emptyError: "不能上传空文件",
        paused: "暂停中",
        waiting: "等待中",
        cmd5: "计算md5",
        merging: "正在转码"
      },
      fileStatusText: (status, response) => {
        return this.statusTextMap[status];
      },
      saveBtnShow: false,
      queryBtnShow: true,
      queryCheckShow: false,
      // queryCheckStatus: false,
      checkStatus: "校验中, 请稍等",
      uuid: "",
      file_path: ""
    };
  },
  mounted() {
    Bus.$on("openUploader", query => {
      this.params = query || {};
      if (this.$refs.uploadBtn) {
        $("#global-uploader-btn").click();
      }
    });
  },
  computed: {
    //Uploader实例
    uploader() {
      return this.$refs.uploader.uploader;
    }
  },
  methods: {
    onFileAdded(file) {
      // this.panelShow = true;
      this.queryCheckShow = false;
      this.saveBtnShow = false;
      this.queryBtnShow = false;
      this.computedMD5(file);

      // Bus.$emit("fileAdded");
    },

    onFileProgress(rootFile, file, chunk) {
      console.log(
        `上传中 ${file.name}，chunk：${chunk.startByte /
          1024 /
          1024} ~ ${chunk.endByte / 1024 / 1024}`
      );
    },

    onFileSuccess(rootFile, file, response, chunk) {
      let res = JSON.parse(response);
      file.success = true;
      // 文件完成上传, 文件合并的标志
      if (res.needMerge === "true") {
        this.statusSet(file.id, "merging");
        let formData = new FormData();
        formData.append("filename", file.name);
        formData.append("identifier", arguments[0].uniqueIdentifier);
        formData.append("totalSize", file.size);
        formData.append("timeStamp", res.timeStamp);
        const instance = this.$axios.create({
          headers: {
            "Content-Type": "multipart/form-data"
          }
        });
        instance
          .post("http://127.0.0.1:8000/fileUpload/fileMerge", formData)
          .then(res => {
            console.log(res);
            this.statusRemove(file.id);
            this.statusSet(file.id, "success");
            this.queryBtnShow = true;
            Bus.$emit("fileSuccess");
            let formData2 = new FormData();
            formData2.append("fpath", res.data.filePath);
            formData2.append("fname", res.data.fileName);
            const instance2 = this.$axios.create({
              headers: {
                "Content-Type": "multipart/form-data"
              }
            });
            instance2
              .post("http://127.0.0.1:8000/fileUpload/textCheck", formData2)
              .then(res => {
                this.uuid = res.data.uuid;
                this.file_path = res.data.file_path;
                console.log("-------------");
                console.log(res);
                console.log("file_path::", res.data.file_path);
                // console.log("res:", res);
                console.log(this.file_path);
                // this.statusRemove(file.id);
                // this.statusSet(file.id, "checking");
                // 定时发送请求,看检验是否完成
                let interval = window.setInterval(() => {
                  setTimeout(() => {
                    let formData3 = new FormData();
                    formData3.append("file_uuid", res.data.uuid);
                    const instance3 = this.$axios.create({
                      headers: {
                        "Content-Type": "multipart/form-data"
                      }
                    });
                    instance3
                      .post(
                        "http://127.0.0.1:8000/fileUpload/check_result",
                        formData3
                      )
                      .then(res => {
                        console.log("校验中,请稍等...");
                        if (res.data.code == "200") {
                          console.log("校验完成");
                          clearInterval(interval);
                          // this.statusRemove(file.id);
                          // this.statusSet(file.id, "checkSuccess");
                          this.checkStatus = "校验完成";
                          this.saveBtnShow = true;
                        }
                      });
                  }, 0);
                }, 1000);
              });
          })
          .catch(function(error) {
            console.log(error);
          });
      }
    },
    onFileError(rootFile, file, response, chunk) {
      this.$message({
        message: response,
        type: "error"
      });
    },
    /**
     * 计算上传文件的md5, 实现断点续传和秒传
     */
    computedMD5(file) {
      let fileReader = new FileReader();
      let time = new Date().getTime();
      let blobSlice =
        File.prototype.slice ||
        File.prototype.mozSlice ||
        File.prototype.webkitSlice;
      let currentChunk = 0;
      const chunkSize = 10 * 1024 * 1000;
      let chunks = Math.ceil(file.size / chunkSize);
      let spark = new SparkMD5.ArrayBuffer();

      this.statusSet(file.id, "md5");
      file.pause();
      // $('.uploader-file-action').css('display', 'none');
      loadNext();

      fileReader.onload = e => {
        spark.append(e.target.result);

        currentChunk++;
        if (currentChunk < chunks) {
          console.log(
            `第${currentChunk}分片解析完成, 开始第${currentChunk +
              1} / ${chunks}分片解析`
          );
          loadNext();

          // 实时展示MD5的计算进度
          this.$nextTick(() => {
            $(`.myStatus_${file.id}`).text(
              "校验MD5 " + ((currentChunk / chunks) * 100).toFixed(0) + "%"
            );
          });
        } else {
          let md5 = spark.end();
          this.computeMD5Success(md5, file);
          spark.destroy(); // 释放缓存
          console.log(
            `MD5计算完毕：${file.name} \nMD5：${md5} \n分片：${chunks} 大小:${
              file.size
            } 用时：${new Date().getTime() - time} ms`
          );
        }
      };

      fileReader.onerror = function() {
        this.error(`文件${file.name}读取出错，请检查该文件`);
        file.cancel();
      };

      function loadNext() {
        let start = currentChunk * chunkSize;
        let end =
          start + chunkSize >= file.size ? file.size : start + chunkSize;

        fileReader.readAsArrayBuffer(blobSlice.call(file.file, start, end));
      }
    },
    computeMD5Success(md5, file) {
      file.uniqueIdentifier = md5; // 将文件md5赋值给文件唯一标识
      file.resume();
      this.statusRemove(file.id);
    },
    fileListShow() {
      let $list = $("#global-uploader .file-list");

      if ($list.is(":visible")) {
        $list.slideUp();
      } else {
        $list.slideDown();
      }
    },
    close() {
      this.uploader.cancel();
    },

    /**
     * 新增的自定义的状态: 'md5'、'transcoding'、'failed'
     * @param id
     * @param status
     */
    statusSet(id, status) {
      let statusMap = {
        md5: {
          text: "校验MD5",
          bgc: "#fff"
        },
        merging: {
          text: "正在转码",
          bgc: "#e2eeff"
        },
        transcoding: {
          text: "转码中",
          bgc: "#e2eeff"
        },
        failed: {
          text: "上传失败",
          bgc: "#e2eeff"
        },
        success: {
          text: "上传成功",
          bgc: "#e2eeff"
        },
        checking: {
          text: "正在校验",
          bgc: "#e2eeff"
        },
        checkSuccess: {
          text: "校验完成",
          bgc: "#e2eeff"
        }
      };

      this.$nextTick(() => {
        $(`<p class="myStatus_${id}"></p>`)
          .appendTo(`.file_${id} .uploader-file-status`)
          .css({
            position: "absolute",
            top: "-16px",
            left: "0",
            right: "0",
            bottom: "0",
            zIndex: "1",
            backgroundColor: statusMap[status].bgc
          })
          .text(statusMap[status].text);
      });
    },
    statusRemove(id) {
      this.$nextTick(() => {
        $(`.myStatus_${id}`).remove();
      });
    },

    error(msg) {
      this.$notify({
        title: "错误",
        message: msg,
        type: "error",
        duration: 2000
      });
    },
    queryCheck: function(uuid) {
      console.log("uuid::", uuid);
      console.log("file_path::--------", this.file_path);
      // if (uuid === "") {
      //   this.queryCheckStatus = true;
      //   return;
      // }
      let formData = new FormData();
      formData.append("file_uuid", uuid);
      const instance = this.$axios.create({
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });
      instance
        .post("http://127.0.0.1:8000/fileUpload/check_result", formData)
        .then(res => {
          // console.log("点击了查询校验状态按钮");
          if (res.data.code == "200") {
            // this.queryCheckStatus = false;
            this.checkStatus = "校验完成";
            this.queryCheckShow = true;
          } else {
            this.checkStatus = "正在校验中";
            this.queryCheckShow = true;
          }
        });
    },
    download_check_result() {
      let formData = new FormData();
      formData.append("file_path", this.file_path);
      const instance = this.$axios.create({
        headers: {
          "Content-Type": "multipart/form-data"
        },
        responseType: "blob"
      });
      instance
        .post("http://127.0.0.1:8000/fileUpload/file_download", formData)
        .then(response => {
          if (!response) {
            return;
          }
          let url = window.URL.createObjectURL(new Blob([response.data]));
          let link = document.createElement("a");
          link.style.display = "none";
          link.href = url;
          link.setAttribute("download", "校验结果.txt");

          document.body.appendChild(link);
          link.click();
        });
    }
  },
  watch: {},
  destroyed() {
    Bus.$off("openUploader");
  }
};
</script>

<style scoped lang="scss">
#global-uploader {
  // position: fixed;
  z-index: 20;
  max-width: 1000px;
  margin: 10px auto;

  background: #fff;
  padding: 10px;
  h2 {
    padding: 30px 0;
    text-align: center;
    font-size: 20px;
  }
  .uploader-app {
    width: 880px;
    padding: 15px;
    margin: 20px auto 0;
    font-size: 14px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 4);
  }

  ul li {
    list-style-type: none;
  }
  li div {
    left: -19px;
  }
}
.file-panel {
  background-color: #fff;
  border: 1px solid #e2e2e2;
  border-radius: 7px 7px 0 0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);

  .file-title {
    display: flex;
    height: 40px;
    // line-height: 40px;
    padding: 0 15px;
    border-bottom: 1px solid #ddd;

    .operate {
      flex: 1;
      text-align: right;
    }
  }

  .file-list {
    position: relative;
    height: 240px;
    overflow-x: hidden;
    overflow-y: auto;
    background-color: #fff;

    > li {
      background-color: #fff;
    }
  }

  &.collapse {
    .file-title {
      background-color: #e7ecf2;
    }
  }
}

.no-file {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
}
.uploader-btn {
  margin-right: 4px;
  color: #fff;
  padding: 6px 16px;
}
#global-uploader-btn {
  border: 1px solid #409eff;
  background: #409eff;
}
#global-uploader-dir-btn {
  border: 1px solid #67c23a;
  background: #67c23a;
}
.save-result {
  position: absolute;
  margin-top: -24px;
  margin-left: 700px;
  z-index: 10;
}

.query_check {
  position: absolute;
  margin-left: 700px;
  margin-top: -50px;
  z-index: 10;
}

.queryCheckShow {
  margin-left: 10px;
  color: red;
  font-size: 12px;
}
</style>
