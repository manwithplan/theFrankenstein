"""

the playersStream class defines a type of player that we can use to play snippet files.
It can play a sequence of snippets in a certain order, by allowing you to write to a 'stream'.
This stream can be used for real time playback and audio selection.

- openStream : opens a non-blocking stream with reference to the correct audio properties and
a callback function.

- closeStream : closes the stream correctly.

- writeToPipeline : takes in a list of audiosegments and adds it to the pipeline and pipelineNames lists

- callback : the callback function that writes the audiosegments from pipeline continuously to the stream.
If no files are left in the pipeling we write recurrent chunks of silence, thus ensuring that the stream never
has to close. 

- getPipelineInfo : returns both the pipeline as the pipelineNames lists as lists.

- getAudioProperties : takes in a fileName and sets the audioProperties to it's audioProperties.

- getAudioPropertiesFromPipeline : takes the first element of the pipeline and sets it's audio properties 
to the object's audio properties

"""

from Settings.Settings import rootURL, musicSnippetsURL, shutterSpeed

import os
import pyaudio
import pydub


class playerStream:
    def __init__(self):
        super().__init__()

        self.snippetURL = musicSnippetsURL

        # initializing the audio properties
        self.format = 8
        self.sampleWidth = 2
        self.channels = 2
        self.rate = 44100
        self.chunkSize = 22050

        # initializing pyAudio objects
        self.p = pyaudio.PyAudio()
        self.stream = None

        # segment is what is written to the stream in a loop. We initialize it with silence (of the correct number of frames,
        # and audio properties we will be using) and afterwards either write chunks of audio data or chunks of silence to,
        # depending on whether there is music in the pipeline. By cutting the data we've already used we can always keep
        # writing to the stream.
        self.segment = pydub.AudioSegment.silent(
            duration=shutterSpeed * 1000, frame_rate=self.rate
        ).set_channels(2)

        # pipeline is a list, used to store a sequence of audio snippets, that can then be written to the stream.
        # pipelineNames stores the fileNames for post playback analysis.
        # pipelineCounter is used to track at what point in the pipeline we are reading/writing.
        self.pipeline = [
            pydub.AudioSegment.silent(
                duration=shutterSpeed * 1000, frame_rate=self.rate
            ).set_channels(2)
        ]
        self.pipelineNames = []
        self.pipelineCounter = 0

    def openStream(self):
        # initializing a pyaudio object and opening a media stream with variables populated by one of the snippets.
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunkSize,
            stream_callback=self.callback,
        )

        # print("stream opened with : FORMAT : {} - CHANNELS : {} - RATE : {}".format(self.format, self.channels, self.rate))

    def closeStream(self):

        # closing both the stream object and the pyAudio object
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # print("stream closed")

    def writeToPipeline(self, fileNames):

        # print( "fileNames : " + str(fileNames) )

        # taking a list of fileNames and writing it to the Snippets list as audioSegments on one hand and storing the fileNames in pipelineNames.
        for fileName in fileNames:
            # load an audioSegment into the pipeline, with audio properties set to the ones we prefer.
            self.pipeline.append(
                pydub.AudioSegment.from_file(os.path.join(self.snippetURL, fileName))
                .set_sample_width(self.sampleWidth)
                .set_channels(self.channels)
                .set_frame_rate(self.rate)
            )
            # print('{} properties : format - {} | channels : {} | rate : {}'.format(fileName, self.p.get_format_from_width(self.pipeline[-1].sample_width), self.pipeline[-1].channels, self.pipeline[-1].frame_rate))
            # store the fileNames in pipelineNames
            self.pipelineNames.append(fileName)
            # print("pipeline : " + str(self.pipeline) )

        if self.segment is None:
            # if no segment has been loaded yet, we'll write the first file in the pipeLine to segment.
            self.segment = self.pipeline[self.pipelineCounter]
            # print('first segment loaded')
            # print('segment : {} '.format(self.segment))

    def fadeAndStopPlayback(self):
        # the goal here is to softly fade out from the music. We do this by cutting the remaining snippets from the
        # pipeline bar, in this case 4 snippets in order to promote continuity, and then editing these to fade out.
        # We fade out by crossfading the last audiosegment in the pipeline with silence. The generated silence has
        # the same length and uses a crossfade of the same length as the  last element in the pipeline in order to
        # transition smoothly. 100 ms is then subtracted to avoid pops and clicks.

        self.pipeline = self.pipeline[: self.pipelineCounter + 4]
        self.pipeline[-1] = self.pipeline[-1].append(
            pydub.AudioSegment.silent(duration=len(self.pipeline[-1])),
            crossfade=len(self.pipeline[-1]) - 100,
        )

        self.pipelineNames = self.pipelineNames[: self.pipelineCounter + 4]

    def fadeAndMix(self, fileNames, location=0):
        # the goal is to crossfade into a new piece of music. The basic mechanism is to delete the remaining snippets
        # from the pipeline, bar 1, and the rewriting the last one to crossfade with the targetted snippet of the next
        # piece.
        #
        # Important is that you have the crossfade the shorter snippet to the longer one. That's what the if else block
        # is for
        #
        # the location variable is to add the functionality of choosing where exactly in the next track we start playback.

        try:
            self.pipeline = self.pipeline[: self.pipelineCounter + 4]
            self.pipelineNames = self.pipelineNames[: self.pipelineCounter + 4]

            firstSnippet = (
                pydub.AudioSegment.from_file(
                    os.path.join(self.snippetURL, fileNames[location])
                )
                .set_sample_width(self.sampleWidth)
                .set_channels(self.channels)
                .set_frame_rate(self.rate)
            )

            if len(self.pipeline[-1]) >= len(firstSnippet):

                # trimming the original snippet to the same length as the snippet to be appended
                self.pipeline[-1] = self.pipeline[-1][: len(firstSnippet)]

                self.pipeline[-1] = self.pipeline[-1].append(
                    firstSnippet, crossfade=len(self.pipeline[-1]) - 100
                )
                self.writeToPipeline(fileNames[(location + 1) :])

            else:
                self.pipeline[-1] = self.pipeline[-1].append(
                    firstSnippet, crossfade=len(self.pipeline[-1]) - 100
                )
                self.writeToPipeline(fileNames[(location + 1) :])

        except Exception as e:
            print("fadeAndMix can't be executed because of {}".format(e))

    def callback(self, in_data, frame_count, time_info, status):

        # the callback function is called in a seperate thread from the audioStream object. It writes a set number of frames to the stream before it is called again.
        # If at any point no new data is found to be written to the stream, the stream will turn inactive.

        # Because the pyAudio stream expects a number of frames from a byte like object we have to convert the AudioSegment (pydub) to raw_data. After which we select
        # the frames we need in milliseconds rather than frames. So first we convert frames to ms.
        time = (frame_count / self.segment.frame_rate) * 1000.0

        # we then select the part of the audioSegment to be written in accordance to the chunk size.
        data = self.segment[:time].raw_data

        # After which we cut the part written from the original file, so as not to have any duplicate frames.
        self.segment = self.segment[time:]

        # If the callback function runs out of frames to read, we check the pipeline object to see if there are more available.
        if self.segment.frame_count() < frame_count:
            # print('callback')

            # print('segment frame count : {} and frame_count : {}'.format(self.segment.frame_count(), frame_count))

            try:
                # we update the counter as well, so as to keep track of where we are.
                self.pipelineCounter += 1

                # by simply appending the 2 audioSegments to each other we can continue the playback seamless for as long as the pipeLine is not empty.
                self.segment = self.segment + self.pipeline[self.pipelineCounter]
                # print('next snippet loaded')
            except Exception as e:
                # this part of the callback function is responsible for not closing the stream when we are currently out of audio to play. It subtracts
                # from the pipLineCounter variable what the last step added, and adds silence to the end of the segment we read from.

                # print('error : {}, silent running, length pipeline : {}, pipeline counter : {}'.format(e, len(self.pipeline), self.pipelineCounter))
                self.pipelineCounter -= 1
                self.segment = self.segment + pydub.AudioSegment.silent(duration=time)

        return (data, pyaudio.paContinue)

    def getPipelineInfo(self):
        return [self.pipeline, self.pipelineNames]

    def getFutureSnippet(self, distance):
        """
        returns a music snippet that will be played in the near future. By setting the distance
        some time is given for the similaritysearch to be completed.
        """
        return self.pipelineNames[self.pipelineCounter + distance]

    def getAudioProperties(self, audioFile):

        # this function will take in a fileName string that corresponds with the path of the file.
        temp = pydub.AudioSegment.from_file(self.snippetURL + audioFile)

        # from it, it will determing the audio properties
        self.format = temp.sample_width
        self.channels = temp.channels
        self.rate = temp.frame_rate

        # print("FORMAT : {} - CHANNELS : {} - RATE : {}".format(self.format, self.channels, self.rate))

    def getAudioPropertiesFromPipeline(self):

        # this function will take in a fileName string that corresponds with the path of the file.
        temp = self.pipeline[0]

        # from it, it will determing the audio properties
        self.format = self.p.get_format_from_width(temp.sample_width)
        self.channels = temp.channels
        self.rate = temp.frame_rate

        # print("FORMAT : {} - CHANNELS : {} - RATE : {}".format(self.format, self.channels, self.rate))

